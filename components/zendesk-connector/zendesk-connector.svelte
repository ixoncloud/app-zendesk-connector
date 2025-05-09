<script lang="ts">
  import type {
    ComponentContext,
    BackendComponentClient,
    FormDialogResult,
  } from '@ixon-cdk/types';
  import { DateTime } from 'luxon';
  import { onMount } from 'svelte';

  export let context: ComponentContext;

  type Ticket = {
    createdAt: string;
    description: string;
    id: number;
    priority: string;
    status: string;
  };

  let webFunctionsClient: BackendComponentClient;
  let tickets: Ticket[] = [];
  let loading = true;
  let error = '';

  let contentScrollTop: number;
  let tableWrapper: HTMLDivElement;
  let tableWidth = 0;

  onMount(async () => {
    webFunctionsClient = context.createBackendComponentClient();
    await getTickets();
    const interval = setInterval(async () => {
      await getTickets();
    }, 60000);

    return () => {
      clearInterval(interval);
    };
  });

  const onScroll = () => {
    contentScrollTop = Math.max(0, tableWrapper.scrollTop);
  };

  function createTooltip(element: HTMLElement, text: string): void {
    context.createTooltip(element, {
      message: context.translate(text),
    });
  }

  async function getTickets() {
    loading = true;
    const response = await webFunctionsClient.call('get_zendesk_tickets');
    if (response.data.status === 'error') {
      error = response.data.message;
    } else {
      tickets = response.data.tickets || [];
    }
    loading = false;
  }

  async function openFormDialog() {
    const result = await context.openFormDialog({
      title: 'Request Support',
      inputs: [
        {
          key: 'description',
          type: 'Text',
          label: 'How can we help?',
          required: true,
          translate: false,
        },
        {
          key: 'priority',
          type: 'Selection',
          options: [
            { value: 'low', label: 'Low' },
            { value: 'normal', label: 'Normal' },
            { value: 'high', label: 'High' },
            { value: 'urgent', label: 'Urgent' },
          ],
          label: 'Priority?',
          required: true,
        },
      ],
      submitButtonText: context.translate('SUBMIT__FORM'),
    });
    if (result) {
      handleSubmit(result as FormDialogResult);
    }
  }

  async function openSuccessDialog() {
    const result = await context.openAlertDialog({
      title: 'Support Requested',
      message:
        'Your support request has been submitted. Please check your email for a confirmation. It can take a few minutes for your ticket to show up in this overview',
    });
  }

  async function openDescriptionDialog(ticket: Ticket) {
    const result = await context.openAlertDialog({
      title: 'Ticket Details',
      message: ticket.description,
    });
  }

  async function handleSubmit(result: {
    value: { description: string; priority: string };
  }) {
    const newTicket = {
      description: result.value.description,
      priority: result.value.priority,
    };

    const createResponse = await webFunctionsClient.call('create_ticket', {
      ticket_description: newTicket.description,
      ticket_priority: newTicket.priority,
    });

    if (createResponse.data.status === 'success') {
      await openSuccessDialog();
    }
  }

  function formatDateTime(occurredOn: string) {
    const milliseconds = DateTime.fromISO(occurredOn).toMillis();
    return DateTime.fromMillis(milliseconds, {
      locale: context.appData.locale,
      zone: context.appData.timeZone,
    }).toLocaleString({
      ...DateTime.DATETIME_SHORT_WITH_SECONDS,
    });
  }
</script>

<div class="card">
  {#if loading}
    <div class="card-content">
      <p>loading...</p>
    </div>
  {/if}
  {#if error}
    <div class="card-content">
      <p>{error}</p>
    </div>
  {/if}
  {#if !loading && !error}
    <div class="card-header">
      <h3 class="card-title">Support Tickets</h3>
      <div class="card-header-actions">
        <button
          class="icon-button"
          on:click={openFormDialog}
          use:createTooltip={'Request support'}
        >
          <svg
            enable-background="new 0 0 24 24"
            height="24px"
            viewBox="0 -960 960 960"
            width="24px"
            fill="currentColor"
          >
            <path
              xmlns="http://www.w3.org/2000/svg"
              d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"
            />
          </svg>
        </button>
      </div>
      <!-- <button class="button primary add-ticket-button" on:click={openFormDialog}
        >Request support</button
      > -->
    </div>
    <div class="card-content">
      {#if contentScrollTop > 0}
        <div class="table-header-drop-shadow" style="width: {tableWidth}px" />
      {/if}
      <div class="table-header-padding-coverup table-head" />
      <div class="table-header-padding-coverup table-body" />
      <div
        class="table-wrapper"
        on:scroll={onScroll}
        bind:this={tableWrapper}
        bind:clientWidth={tableWidth}
      >
        <table class="base-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Description</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Created at</th>
            </tr>
          </thead>

          <tbody>
            {#each tickets as ticket}
              <tr>
                <td>{ticket.id}</td>
                <td>
                  {ticket.description.slice(
                    0,
                    50
                  )}<!-- Display only the first 50 characters -->
                  {#if ticket.description.length > 50}
                    ... <button
                      class="details-button"
                      on:click={openDescriptionDialog(ticket)}
                      >View Details</button
                    >
                  {/if}</td
                >
                <td>{ticket.status}</td>
                <td>{ticket.priority}</td>
                <td
                  >{ticket.createdAt
                    ? formatDateTime(ticket.createdAt)
                    : ''}</td
                >
                <td />
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>

<style lang="scss">
  @import './styles/_card';
  @import './styles/_button';
  @import './styles/_icon-button';

  .card-header {
    display: flex;
    flex-direction: row;
    align-items: baseline;
    justify-content: space-between;

    .card-header-actions {
      padding: 8px;

      @media print {
        display: none;
      }
    }

    .button {
      display: flex;
      flex-direction: row;
      align-items: center;
      padding-right: 12px;
      padding-left: 8px;
      background-color: var(--accent);
      line-height: 32px;
      font-size: 14px;
      color: var(--accent-color);
    }
  }

  .card-content {
    position: relative;
  }

  .table-header-padding-coverup {
    position: absolute;
    left: 0;
    top: 0;
    width: 8px;
    background: var(--card-bg);

    &.table-head {
      height: 34px;
      z-index: 15;
    }

    &.table-body {
      bottom: 16px;
      z-index: 5;
    }
  }

  .details-button {
    padding: 0;
    margin: 0;
    font-size: 12px;
    line-height: 1;
    height: 20px;
    min-width: 0;
    border: none;
    background: none;
    color: var(--primary);
    text-decoration: underline;
    cursor: pointer;
  }

  .table-header-drop-shadow {
    position: absolute;
    left: 0;
    top: 0;
    height: 36px;
    width: 100%;
    background: var(--card-bg);
    box-shadow: 0 2px 2px 0 var(--card-border-color);
    z-index: 10;
  }

  .table-wrapper {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    padding: 8px;
    overflow: auto;
    overflow-anchor: none;
  }

  table {
    border-spacing: 0;
    width: 100%;

    tbody td,
    tbody th {
      @for $col from 1 through 30 {
        &:nth-child(#{$col}) span {
          min-width: var(--column-#{$col}-width);
        }
      }
    }

    tbody tr:nth-child(odd) {
      background-color: color-mix(in srgb, transparent, currentcolor 4%);
    }

    tbody tr {
      outline: none;
    }

    tbody {
      th span,
      td span {
        display: inline-block;
        min-width: 4em;
      }
    }

    tr {
      td {
        .old-value,
        .no-value {
          color: lightgray;
        }

        word-wrap: break-word;

        // white-space: nowrap;
        padding-right: 24px;
      }

      th {
        padding-right: 24px;
      }
    }

    thead th {
      position: sticky;
      white-space: nowrap;
      background: var(--card-bg);
      top: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 7em;
      z-index: 10;
      text-align: left;
    }

    tbody th {
      white-space: nowrap;
      text-align: left;
      font-weight: 400;
      padding-right: 4px;
    }

    abbr[title] {
      text-decoration-style: dotted;
      text-decoration-line: underline;
    }
  }
</style>

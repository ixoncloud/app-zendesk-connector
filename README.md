# Zendesk Connector App

This workspace contains the Zendesk Connector App for IXON Cloud. It can be used to present and create machine and user specific service tickets in the IXON Cloud. It is based on the [IXON Cloud Custom Component Development Kit](https://developer.ixon.cloud/docs/custom-components) and [IXON Cloud Backend Component Workspace](https://github.com/ixoncloud/backend-component-workspace). Note that this app is built with [Svelte](https://svelte.dev/), [Typescript](https://www.typescriptlang.org/), [SCSS](https://sass-lang.com/) and [Python](https://www.python.org/). It requires you to be familiar with the [Node.js](https://nodejs.org/) ecosystem.

## Testing locally

Install the dependencies...

```sh
npm install
```

...login to your IXON Cloud account...

```sh
npx cdk login
```

...and run the simulator:

```sh
npx cdk simulate zendesk-connector
```

...this opens the simulator app in a browser and builds the component in watch-mode, which means that any changes to the component source files will trigger a rebuild and will auto-reload the simulator.

To run the Cloud Functions call:

```sh
make run
```

...no additional commands are required, as this is automatically sets up your virtual environment and installs dependencies.

## Documentation

To check out docs and examples on how to develop an App, visit [Custom Component Development Docs](https://developer.ixon.cloud/docs/custom-components) and [Cloud Functions Development Docs](https://developer.ixon.cloud/docs/cloud-functions-introduction).

The [@ixon-cdk/runner](https://www.npmjs.com/package/@ixon-cdk/runner) page has a complete overview of all commands that can be run in a component workspace project.

## Context config

```json
{
  "values": {
    "zendesk_email": "x",
    "zendesk_token": "y",
    "zendesk_subdomain": "z",
    "custom_fields": [
      {
        "ixon": "comSerial",
        "zendesk": 11910782571793
      }
    ]
  }
}
```

- zendesk_email: is the email address of the zendesk admin
- zendesk_token: is the token of the zendesk admin: In Admin Center, click Apps and integrations in the sidebar, then select APIs > Zendesk API. Click the Add API token button to the right of Active API tokens. The token is generated and displayed.
- zendesk_subdomain: is the subdomain of the zendesk admin: https://subdomain.zendesk.com
- custom_fields: is used to map IXON custom field to a Zendesk custom field to automatically add the field value to a Zendesk ticket upon creation. You can add multiple mappings to this array.
  - Create Zendesk custom fields in the Admin Center / Objects and rules / Tickets / Fields
  - create IXON ustom fields in the Admin app / Custom fields

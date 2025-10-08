---
title: Telegram Bot for  GitHub Actions
date: "2025-10-07"
description: Make a Telegram bot with Node.js and use it with GitHub Actions for sending notifications to you about the repo.
tldr: Making GitHub Actions with Js Code
toc: true
---
## Telegram
[Telegram](https://telegram.org/) is a cloud-based mobile and desktop messaging app with a focus on security and speed. It is free to use and extensively hackable. It also has a good bot support system. The API is also easy to implement and has many wrappers for building bots with the API.

## GitHub Actions
[GitHub Actions](https://github.com/features/actions) is a CI/CD runtime for your GitHub repository. You can run almost anything from scripts to docker containers. You can build, test and deploy your code with GitHub Actions. All these actions are called workflows and workflows differ in the job they're doing. These maybe test workflows, build ones or deployment ones. You can find all the actions on GitHub in the [marketplace](https://github.com/marketplace?type=actions)

## Building the Bot
### Prerequisites
- Basic JavaScript Knowledge
- Basic GitHub Knowledge
- Telegram Account
  
> There are templates for building actions. Here we're gonna start from scratch

### Environment Setup
- **Node**, You can download node from their [website](https://nodejs.org/en/download/)
- NPM comes with node, so you don't have to worry about it.
- Initialize the Project
```shell
$ git init ## initialize a new git repository for version management
---
$ npm init
```
- **dotenv**, Dotenv can be downloaded via
```shell
$ npm i dotenv
---
$ yarn add dotenv
```
- **node-telegram-bot-api**, node-telegram-bot-api is a simple wrapper for building telegram bots. You can download it via
```shell
$ npm i node-telegram-bot-api
---
$ yarn add node-telegram-bot-api
```
- **@zeit/ncc**, NCC is a Simple CLI for compiling a Node.js module into a single file, together with all its dependencies, GCC-style. It's a dev dependency and can be downloaded
```shell
yarn add --dev @zeit/ncc
---
npm i -D @zeit/ncc
```

# Stonks 📈📊🤖 Bot: simple stock market tracking telegram bot service

The idea 💡 of this project is simple:

> To be able to track prices of certain stock market instruments (or even currencies 💹, crypto tokens 🪙) by simply sending tracking order to a telegram bot and __receiving updates__ when price of a stock reaches specified value.

The project is open-sourced with the idea that those who want to have a similar service - could simply fork the repo and deploy it to own server by changing just a few environment variables.

While I don't plan to add every stock market or cryptocurrency data provider that exists, some of the ones I use will be added soon (maybe 🤪):

- [x] Alpha-Vantage API
- [ ] Binance API
- [ ] Tinkoff Investments API
- [ ] CBR (maybe maybe maybe)

So if you need more data providers or any third party APIs, you can just fork the repository and add as many as you need!

## Architecture

Main components:

- Database or some BaaS service that stores tracking orders & financial data ([Supabase](supabase.com) used as backend)
- Telegram Bot (dockerized) that adds new tracking orders and sends notifications when price reached target value (which should be specified by user)
- Updater - a serverless function that updates Database using api providers

### DB Schema

### Telegram Bot (pyrogram)

### Serverless DB functions (supabase)

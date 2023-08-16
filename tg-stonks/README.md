# Stonks bot

TODO:

- [ ] add more stock market data providers:
  - [ ] wallstreet python package
  - [ ] tinkoff investments

- [ ] impl. or modify `/track <ticker> <price>` - for stocks (*and bonds* ***maybe*** ???), `/track_currency <sign_or_flag> <sign_or_flag>`, `/track_crypto <crypto_code> <crypto_code>`
- [ ] reading environment variables from `.env` file (use `python-dotenv`)
- [ ] impl. `/start` command: show "hello, friend" message, if deep_link_code passed - it should query db and auth user with OAuth
- [ ] impl. `/sign_out` command: deletes account after confirmation (via email ov)
- [ ] modify `/auth` command: should redirect to a web service (frontend - second part of the app) that would OAuth user via Google, GitHub, Discord, Email-Password
  - [ ] temporary solution: force user to confirm via email and password
- [ ] impl. `/portfolio` command: show tracking stocks and currencies with stats, also CBR stats (for RF users)
- [ ] impl. `/forex` command: list of currency-pairs tracked
- [ ] impl. `/stocks` command: list of currently tracked stocks and bonds
- [ ] impl. `/settings` command: shows what settings (current auth status) could be changed, also what tokens could be specified
- [ ] impl. `/add_token` command: replies with list of tokens provided (`tinkoff investments` "read-only" token - is the only choice for now)
  - [ ] research: use of *Binance Token* possibility  
- [ ] provide docker file
- [ ] impl. **scheduling and notification mechanism** using something like *supabase / firebase functions*
- [ ] impl. `/crypto` show tracked 

Secondary stuff:

- [ ] add CI for python
- [ ] add linter to the project
- [ ] add linting to CI
- [ ] add [Hypothesis](https://hypothesis.readthedocs.io/en/latest/) property based testing

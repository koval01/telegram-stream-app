
|            🗺 Routes 🗺          |                           🚧 Usage 🚧                         | 🍕 Method 🍕 |
|:--------------------------------:|:------------------------------------------------------------:|:------------:|
|               `/`                |                           Home page.                         |     GET      |
|        `/{channel_name}`         |                         Channel view.                        |  GET, POST   |
|   `/{channel_name}/<int:post>`   |                    For select post by ID.                    |  GET, POST   |
|              `/v`                |                  For send view to Telegram.                  |     POST     |
|        `/i/<path:path>`          |                         Proxy t.me/i/...                     |     GET      |
|        `/js/<path:path>`         |                         Proxy t.me/js/...                    |     GET      |
|         `/favicon.ico`           |                   Redirect to local static.                  |     GET      |
|   `/{proxy_route}/<path:url>`    | Proxy other source (example /proxy_route/host.net/path/...). |  GET, POST   |

---

- Just [deploy](#deployments) this repository for testing. 🧪

### Deployments



<details><summary>Heroku.com 🚀</summary>
<br>

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/koval01/telegram-stream-app)
</details>
 
<details><summary>Replit.com 🌀</summary>
<br>

[![Run on Repl.it](https://repl.it/badge/github/koval01/telegram-stream-app)](https://repl.it/github/koval01/telegram-stream-app)
</details>

<details><summary>Zeet.co 💪</summary>
<br>
 
[![Deploy](https://deploy.zeet.co/Flask-Example.svg)](https://deploy.zeet.co?url=https://github.com/koval01/telegram-stream-app)
</details>

#### Adding some other hosting providers too 🤧 soon.

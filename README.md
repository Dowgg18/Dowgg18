<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:21211D,55:28332D,100:CDC733&height=200&section=header&text=Douglas%20Domingos&fontSize=48&fontColor=F9F9F9&fontAlignY=38&desc=Backend%20engineer%20%C2%B7%20systems%20that%20keep%20working%20when%20something%20fails&descAlignY=58&descSize=15" width="100%" />

<a href="https://www.linkedin.com/in/douglas-c-domingos/">
  <img src="https://img.shields.io/badge/LinkedIn-21211D?style=for-the-badge&logo=linkedin&logoColor=CDC733" alt="LinkedIn" />
</a>
<a href="mailto:douglascunhadomingos@gmail.com">
  <img src="https://img.shields.io/badge/Email-21211D?style=for-the-badge&logo=gmail&logoColor=CDC733" alt="Email" />
</a>
<img src="https://img.shields.io/badge/Open%20to%20remote%20work-28332D?style=for-the-badge&logoColor=F9F9F9" alt="Open to remote work" />

</div>

<br/>

I run a multi-tenant SaaS in production (FastAPI, Redis, Postgres and Next.js on
Docker Swarm) with paying customers and nobody else on call. I also build for
clients: a supplement brand's store that goes from checkout to tax invoice on its
own, its creator program, and a trade chamber's portal in three languages.

<br/>

### Kamo, my product

<a href="https://github.com/Dowgg18/kamo-showcase">
  <img src="https://raw.githubusercontent.com/Dowgg18/kamo-showcase/main/assets/01-conversas.jpg" alt="Kamo conversations panel on desktop and mobile" width="100%" />
</a>

A multi-tenant SaaS where an AI agent answers a car dealership's WhatsApp end to
end: it qualifies the buyer, collects the financing details one question at a
time, and hands the conversation to a salesperson at the right moment, with the
history ready. 30,772 messages and 1,602 customers through it between May and
August 2026, almost a quarter of them while the store was closed.
FastAPI, Redis Streams, Supabase Realtime and Next.js on Docker Swarm.
**[Screens and architecture →](https://github.com/Dowgg18/kamo-showcase)**

<br/>

### Built for clients

The code belongs to the clients, so these repositories are write-ups: screens,
architecture and the decisions that hold each system up.

<table>
  <tr>
    <td width="33%" valign="top">
      <a href="https://github.com/Dowgg18/4life-nutrition-showcase">
        <img src="https://raw.githubusercontent.com/Dowgg18/4life-nutrition-showcase/main/assets/01-home.jpg" alt="4Life Nutrition store on desktop and mobile" />
      </a>
      <br/><b><a href="https://github.com/Dowgg18/4life-nutrition-showcase">4Life Nutrition · store</a></b>
      <br/><sub>Next.js + Medusa v2. Payment, Brazilian tax invoice, shipping label and WhatsApp alerts, with no one copying data between systems.</sub>
    </td>
    <td width="33%" valign="top">
      <a href="https://github.com/Dowgg18/4life-creators-showcase">
        <img src="https://raw.githubusercontent.com/Dowgg18/4life-creators-showcase/main/assets/10-creator-army.jpg" alt="Creator Army landing page on desktop and mobile" />
      </a>
      <br/><b><a href="https://github.com/Dowgg18/4life-creators-showcase">4Life · Creator Army</a></b>
      <br/><sub>Influencer program: application queue, per-creator coupons and an idempotent commission sweep that corrects itself.</sub>
    </td>
    <td width="33%" valign="top">
      <a href="https://github.com/Dowgg18/camara-brasil-russia-showcase">
        <img src="https://raw.githubusercontent.com/Dowgg18/camara-brasil-russia-showcase/main/assets/02-russo.jpg" alt="Brazil-Russia Chamber portal in Russian" />
      </a>
      <br/><b><a href="https://github.com/Dowgg18/camara-brasil-russia-showcase">Brazil-Russia Chamber</a></b>
      <br/><sub>PT/RU/EN portal on Supabase. Editors paste raw text and get a translated, SEO-ready article; the AI never rewrites the body.</sub>
    </td>
  </tr>
</table>

<br/>

### Open source, pulled out of production

The repositories below are problems my own system surfaced, pulled out and solved
the way I wish I had found them. None of them are demos.

<div align="center">

<a href="https://github.com/Dowgg18/agent-replay-gate">
  <img src="assets/replaygate.svg" alt="replaygate — a pre-deploy regression gate for LLM agents" width="440" />
</a>
<a href="https://github.com/Dowgg18/debounced-webhook-pipeline">
  <img src="assets/burstq.svg" alt="burstq — one ordered unit of work per conversation" width="440" />
</a>

</div>

<br/>

### The problem behind each one

**[burstq](https://github.com/Dowgg18/debounced-webhook-pipeline)** — people type
the way they talk, so one question arrives as four webhook deliveries in three
seconds, and the provider redelivers half of them. Built around three failure
modes that pass every test you would think to write: an idempotency key that
silently eats your retries, a debounce window that dies with the process that
opened it, and a per-conversation lock that stops locking the moment you run two
replicas.

**[replaygate](https://github.com/Dowgg18/agent-replay-gate)** — substring
assertions break on rewording, live-model tests cost money and never repeat, and
"it looked fine in the console" is not a gate. So: replay conversations through
the real code with every I/O boundary sealed under a policy — fake it, count it,
or forbid it — and fail the build the moment a deterministic path reaches for the
model.

**[proven](https://github.com/Dowgg18/unhealthy-until-proven)** — a health check
has three outcomes, not two. A dashboard I owned reported a channel as
**Connected** for two months after it had died, because the status column was
only ever written on the happy path, so it climbed to green and could never come
back down. `measured` / `stale` / `unknown`, and collapsing to a boolean requires
naming what unknown means, at the call site, every time.

**[reachable](https://github.com/Dowgg18/covered-but-unreachable)** — coverage says
the line ran. It does not say production can get there. A unit test that calls a
function directly turns its branches green while the only door real traffic uses
returns three frames earlier. `ORPHANED` is the verdict worth installing it for:
code that runs, passes review, and serves nobody.

<br/>

<div align="center">

### Stack

<img src="https://skillicons.dev/icons?i=python,fastapi,redis,postgres,ts,nextjs,react,tailwind&theme=dark" />
<br/>
<img src="https://skillicons.dev/icons?i=docker,linux,supabase,git,github,vscode&theme=dark" />

</div>

<br/>

### How I work

I write against the model SDK directly rather than through an abstraction
framework, and I keep the interesting failures instead of hiding them — the four
open-source repositories above exist because of that.

<br/>

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Dowgg18/Dowgg18/output/chameleon-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Dowgg18/Dowgg18/output/chameleon.svg" />
  <img alt="A chameleon walking across the contribution graph, taking the colour of each square it eats" src="https://raw.githubusercontent.com/Dowgg18/Dowgg18/output/chameleon-dark.svg" width="100%" />
</picture>

<sub>It takes the colour of whatever it just ate — <a href="scripts/chameleon.py">scripts/chameleon.py</a>, no dependencies.</sub>

<br/><br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:21211D,55:28332D,100:CDC733&height=4&section=footer" width="100%" />

</div>

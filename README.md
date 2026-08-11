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

I run a multi-tenant SaaS in production — FastAPI, Redis, Postgres and Next.js on
Docker Swarm — with paying customers and nobody else on call.

The repositories below are problems that system surfaced, pulled out and solved
the way I wish I had found them. None of them are demos.

<br/>

<div align="center">

<a href="https://github.com/Dowgg18/debounced-webhook-pipeline">
  <img src="https://github-readme-stats.vercel.app/api/pin/?username=Dowgg18&repo=debounced-webhook-pipeline&hide_border=true&bg_color=21211D&title_color=CDC733&icon_color=CDC733&text_color=F9F9F9&show_owner=false" />
</a>
<a href="https://github.com/Dowgg18/agent-replay-gate">
  <img src="https://github-readme-stats.vercel.app/api/pin/?username=Dowgg18&repo=agent-replay-gate&hide_border=true&bg_color=21211D&title_color=CDC733&icon_color=CDC733&text_color=F9F9F9&show_owner=false" />
</a>
<a href="https://github.com/Dowgg18/unhealthy-until-proven">
  <img src="https://github-readme-stats.vercel.app/api/pin/?username=Dowgg18&repo=unhealthy-until-proven&hide_border=true&bg_color=21211D&title_color=CDC733&icon_color=CDC733&text_color=F9F9F9&show_owner=false" />
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
back down.

<br/>

<div align="center">

### Stack

<img src="https://skillicons.dev/icons?i=python,fastapi,redis,postgres,ts,nextjs,react,tailwind&theme=dark" />
<br/>
<img src="https://skillicons.dev/icons?i=docker,linux,supabase,git,github,vscode&theme=dark" />

</div>

<br/>

### Currently

**Kamo** — a multi-tenant SaaS where an AI agent handles customer conversations
end to end for vehicle dealerships: qualifying, collecting financing details, and
handing over to a salesperson at the right moment. Roughly 28k messages and 1.5k
leads through it so far.

I write against the model SDK directly rather than through an abstraction
framework, and I keep the interesting failures instead of hiding them — the three
repositories above exist because of that.

<br/>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:21211D,55:28332D,100:CDC733&height=4&section=footer" width="100%" />

</div>

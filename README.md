# Douglas Domingos

I build backend systems that have to keep working when something fails.

Right now that means a multi-tenant SaaS running in production — FastAPI, Redis,
Postgres and Next.js on Docker Swarm — with paying customers and nobody else on
call. The repositories below are problems that system surfaced, pulled out and
solved the way I wish I had found them.

None of them are demos.

---

## Open source

### [burstq](https://github.com/Dowgg18/debounced-webhook-pipeline) · one ordered unit of work per conversation

People type the way they talk, so one question arrives as four webhook deliveries
in three seconds — and the provider redelivers half of them. This is the Redis
Streams pipeline that collapses that into a single handler call, in order, and
survives a crash in the middle of it.

It is built around three failure modes that pass every test you would think to
write: an idempotency key that silently eats your retries, a debounce window that
dies with the process that opened it, and a per-conversation lock that stops
locking the moment you run two replicas.

`Python` · `Redis Streams` · `asyncio` · `at-least-once delivery`

### [replaygate](https://github.com/Dowgg18/agent-replay-gate) · a pre-deploy gate for conversational agents

Substring assertions break on rewording. Live-model tests are non-deterministic
and cost money. "It looked fine in the console" is not a gate.

So: replay scripted conversations through the real code with every I/O boundary
sealed under a policy — fake it, count it, or forbid it — and fail the build the
moment a path that was supposed to be deterministic reaches for the model. One
exit code, a published rubric, and a report that opens with what broke instead of
with the average.

`Python` · `LLM testing` · `CI` · `regression gates`

### [proven](https://github.com/Dowgg18/unhealthy-until-proven) · a health check has three outcomes, not two

`measured`, `stale`, `unknown`. Almost every monitoring bug is the third one
being quietly folded into one of the first two.

A dashboard I owned reported a channel as **Connected** for two months after it
had died. Four separate mechanisms, each defensible alone, stacked into one lie —
including a status column that was only ever written on the happy path, so it
climbed to green and could never come back down.

The library makes the wrong thing unwritable: `Health` has no truth value,
persistence refuses to record "I could not check", and collapsing to a boolean
requires naming what unknown means, at the call site, every time.

`Python` · `observability` · `SRE` · `fail-safe defaults`

---

## Currently

**Kamo** — a multi-tenant SaaS where an AI agent handles customer conversations
end to end for vehicle dealerships: qualifying, collecting financing details, and
handing over to a salesperson at the right moment. Roughly 28k messages and 1.5k
leads through it so far.

I write against the model SDK directly rather than through an abstraction
framework, and I keep the interesting failures rather than hiding them — the
three repositories above exist because of that.

---

## Stack

Python · FastAPI · Redis · PostgreSQL · TypeScript · Next.js · Docker Swarm · Traefik · Linux

---

## Contact

- **Email** — [douglascunhadomingos@gmail.com](mailto:douglascunhadomingos@gmail.com)
- **LinkedIn** — [douglas-c-domingos](https://www.linkedin.com/in/douglas-c-domingos/)

<sub>Open to backend and platform work, remote.</sub>

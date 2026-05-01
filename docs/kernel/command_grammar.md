<!--
Vendored from agentic-workforce-kernel @ main.
Do not edit — update by re-vendoring from the source repo.
-->

# Command Grammar

## Inter-agent command DSL

Commands are issued by the Director to Workers via the Task object's `description` field
using the following grammar:

```
<command> ::= <verb> <target> [<flags>]
<verb>    ::= RUN | REVIEW | ESCALATE | ABORT | RESUME | REPORT
<target>  ::= <node_name> | <task_id> | "mission"
<flags>   ::= ("--" <key> "=" <value>)*
```

### Examples

```
RUN ingestion --email_id=abc123
REVIEW appraisal --task_id=uuid --strict=true
ESCALATE classification --reason="confidence<0.4"
ABORT mission --reason="cost_exceeded"
RESUME hitl_gate --human_decision=approve
REPORT mission --format=markdown
```

## State mutation rules

- Only the currently assigned Worker may mutate state fields in its domain.
- Shared fields (`total_cost_usd`, `errors`) may be appended to by any node.
- The `terminal_sink` field may only be written by the Router node.
- The `human_decision` field may only be written by the HITL Gate node (after human input).

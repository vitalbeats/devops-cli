DevOps CLI
==========
This repository contains a collect of useful functions, built into a CLI tool that can be used to more easily perform certain maintenance functions on the Vital Beats cluster.

Prerequisites
-------------
The tool requires a number of things to be set up to be useful:

 - The tool makes extensive use for the AWS SDK. As such, you need to be set up with AWS credentials (usually in `~/.aws`) which the tool will pick up and use.
 - For kubernetes functions, the tool makes use of both the `kubectl` program itself, and the underlying credentials (usually in `~/.kube`). You will need to have contexts setup for whichever clusters you are going to interact with.

Common Patterns
---------------
The tool tries to simplify how you refer to resources in the cluster, by describing them in a hierarchy. This hierarchy is externsively used within our AWS Secrets Manager already, so it will be familiar to you if you have had to fetch credentials before. The hierarchy is in the form: `cluster/namespace/object`. So for example for RabbitMQ commands, `scaut-v2-dev/develop/rabbitmq` refers to the RabbitMQ cluster, in the `develop` namespace, within the `scaut-v2-dev` kubernetes cluster.

Commands
--------
Here are the following commands you can execute with the tool:



| Module | Command | Arguments | Description |
|--------|---------|-----------|-------------|
| `aws` | `get-secret-value` | `<secretId ...>` | Fetches the values of given secret(s), returning them as a JSON object, one per line |
| `aws` | `get-secret-as-vars` | `<secretId ...>` | Fetches the values of given secret(s), returning them as shell variables. This is useful to prefix a command with. |
| `aws` | `get-secret-as-env` | `<secretId ...>` | Fetches the values of given secret(s), return them as shell `export` commands, one per line. |
| `rabbitmq` | `replay` | `[rabbitmqCluster] [graveyardQueue]` | Connects to the specified RabbitMQ cluster, and moves all messages on the specified graveyard queue back onto the exchange it belongs to. This can be used to retry already failed transmission messages for example. |

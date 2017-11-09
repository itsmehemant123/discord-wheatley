## wheatley

### Setup

- Install dependencies with:

```bash
pip install -r requirements.txt
```

- Create `auth.json`, and place it inside the `config` folder. Its content should be:

```json
{
   "token": "<your_token>"
}
```

- Create `wheatley.json`, and place it inside the `config` folder. Its content should be:

```json
{
  "database_uri": "mongodb://<uname>:<pwd>@<host>:<port>/<auth_db>",
  "database": "<db>",
  "corpus-folder": "./corpus/"
}
```

_These two files will not be tracked by git, so will not be pushed. Remove their entries from the `.gitignore` if you want otherwise._

### How to run

- Create the `corpus` folder in the project root.

- Run the script with:

```bash
python client.py
```

### How to train

- Download the chat transcripts (_in order_) by typing this in discord:

```
!dwnld <limit> #<channel_name>
```

Where `limit` can either be `all` - _for all messages_, or a number - _the number of messages to download_.

- This should start the download and writing of the transcripts to `yml` files in the `corpus` folder in order.

- Issue the train command with:

```
!train
```

- This should start the training. You'll have to keep track with the console output. If using `nohup` on a server, use the `tail -f` on the logs to see the live progress.

- If errors occur while training, its usually with some weird unicode in the `yml` files. Find out the file name from the error, and fix the error in the file.

- Once finished, you're done.

### Improvements

- The train command has the `chatbot.train`, which can be offloaded to a sub-process, and then switch that sub-process' sysout to a buffer/pipe. Now, in the parent process, use the pipe to send it to another parallely running sub-process to print the pipe content to discord (`bot.edit_message`). This will print out the training process to discord.

- Improve the chat transcript cleanup before writing to yml.

- Switch mongo to mysql/postgres.

- Make a better reply format other than alternate.

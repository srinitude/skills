# No prompt present

Read this example when unsure what to do with an empty request: a message that asks for enhancement but attaches nothing gets a request for the prompt, never an invented one.

The user's words:

```
Can you improve my prompt?
```

Step 1 finds no framed section and no task in the message itself, so no prompt is present. The visible reply:

```
Happy to. Paste the prompt you want improved, and tell me where you plan to
run it if you know (a chat model, a coding agent, an image model). I'll
return an enhanced version without running it.
```

The workflow stops here. Inventing a prompt to enhance would not be enhancement, so nothing else runs until the user supplies the text.

# Decision ledger: orders

One row per decision. A row marked inherited is a choice nobody made on purpose.

| The decision                   | What was chosen         | What it trades away                          | What it risks                                                              | Deliberate or inherited | What would change it                     | Source |
| ------------------------------ | ----------------------- | -------------------------------------------- | -------------------------------------------------------------------------- | ----------------------- | ---------------------------------------- | ------ |
| Sort scope on the orders table | client side, page local | client-side simplicity vs. truthful ordering | a page-local sort that convinces the user they are seeing the true top ten | inherited               | one support ticket about a wrong top ten | -      |

# Evaluation contract

Run all 12 source cases under `without_skill` and `with_skill` with two fresh-context repetitions. Run the 6 training and 6 held-out trigger cases separately. Pass only when every required outcome appears, no veto appears, the decision matches, every rule traces to its source, origin-specific lifecycle differences remain material, and the second apply is a no-op.

Run the local fixture server in an isolated temporary directory. Keep discovery, generation, validation, and transport timing separate. Treat unavailable live activation evidence as an explicit gap rather than a fixture pass.

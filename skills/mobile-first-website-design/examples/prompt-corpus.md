# Verify and select from the public prompt corpus

Run from the skill directory.

## Verify command

`mise run prompt-corpus verify`

## Verify standard output

`{"count":1000,"errors":[],"shards":201,"status":"PASS"}`

## Verify standard error

Empty.

## Verify exit code

`0`

## Select command

`mise run prompt-corpus select advertising-and-social-imagery adapt-and-version assurance-quality`

## Select standard output

Resource gate: run `mise run validate` before using package files named here.

`{"bytes":17787,"domain":"advertising-and-social-imagery","id":"ice-11-04-04","lane":"adapt-and-version","path":"prompts/advertising-and-social-imagery/adapt-and-version/assurance-quality.md","perspective":"assurance-quality","sha256":"9f1c22d3464e6e72eee3b3f8eac5876570f74aaf52590d21df4e9755cdcb7bd6"}`

## Select standard error

Empty.

## Select exit code

`0`

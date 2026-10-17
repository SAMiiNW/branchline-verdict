# Public browser verification

- Checked: 2026-10-17
- Production URL: https://branchline-verdict.pages.dev/
- Browser-visible contract read: `get_case("CASE-1792202937")`
- Observed state: `ROUTED / CLEAR`
- Observed route: question 0 = YES, question 1 = YES, question 2 = NO
- Observed digest: `e9d0eebcd71ebbc72a57c74d3f0b9cdbc08eef370b77c74d233e06f267b6eb27`

The compact-width pass confirmed that the case lookup remains visible and that the public read works without connecting a wallet. The route editor opened with all three questions, six branch targets, and four terminals editable.

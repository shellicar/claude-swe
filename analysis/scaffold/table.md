<style>
.card { border-collapse: collapse }
.card th, .card td { padding: 3px 10px; text-align: left; white-space: nowrap }
.card th { font-weight: bold }
.card .g { border-left: 1px solid #888 }
.card .t { border-top: 1px solid #888 }
.card .h { border-bottom: 1px solid #888; border-top: 1px solid #888 }
.card .u { border-bottom: 1px solid #888 }
.card .s { vertical-align: top }
</style>
<h3>Prompt-scaffolding division (bash only) — SWE-bench Verified hard, Sonnet 5</h3>
<table class="card">
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Hard — 45 <i>Python</i> events (1+ h human effort)</th>
    <th colspan="1" class="h g">Sonnet 5 — bash (control)</th>
    <th colspan="1" class="h g">Sonnet 5 — minimal prompt (pen-down fallback)</th>
    <th colspan="1" class="h g">Sonnet 5 — no ritual (pen-down only)</th>
    <th colspan="1" class="h g">Sonnet 5 — exec tool, no ritual (pen-down only)</th>
  </tr>
  <tr>
    <th rowspan="4" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">🥈 34</td>
    <td class="g">🥈 34</td>
    <td class="g">🥇 <b>38</b></td>
    <td class="g">🥉 33</td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥈 76%</td>
    <td class="g">🥈 76%</td>
    <td class="g">🥇 <b>84%</b></td>
    <td class="g">🥉 73%</td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">🥉 $39.63</td>
    <td class="g">🥈 $33.84</td>
    <td class="g">🥇 <b>$33.22</b></td>
    <td class="g">$40.51</td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">🥉 $1.17</td>
    <td class="g">🥈 $1.00</td>
    <td class="g">🥇 <b>$0.87</b></td>
    <td class="g">$1.23</td>
  </tr>
  <tr>
    <th rowspan="14" class="s t">Stats</th>
    <th class="t">Steps (total)</th>
    <td class="g t">2,206</td>
    <td class="g t">2,111</td>
    <td class="g t">2,045</td>
    <td class="g t">2,067</td>
  </tr>
  <tr>
    <th>Turns/instance (avg)</th>
    <td class="g">49.0</td>
    <td class="g">46.9</td>
    <td class="g">45.4</td>
    <td class="g">45.9</td>
  </tr>
  <tr>
    <th>Cost/turn (avg)</th>
    <td class="g">$0.018</td>
    <td class="g">$0.016</td>
    <td class="g">$0.016</td>
    <td class="g">$0.020</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">725k</td>
    <td class="g">628k</td>
    <td class="g">631k</td>
    <td class="g">804k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">—</td>
    <td class="g">—</td>
    <td class="g">—</td>
    <td class="g">—</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">71.86M</td>
    <td class="g">59.17M</td>
    <td class="g">57.11M</td>
    <td class="g">69.12M</td>
  </tr>
  <tr>
    <th>— non-cached</th>
    <td class="g">4k</td>
    <td class="g">4k</td>
    <td class="g">4k</td>
    <td class="g">4k</td>
  </tr>
  <tr>
    <th>— cache read</th>
    <td class="g">69.78M</td>
    <td class="g">57.23M</td>
    <td class="g">55.19M</td>
    <td class="g">66.89M</td>
  </tr>
  <tr>
    <th>— cache write</th>
    <td class="g">2.08M</td>
    <td class="g">1.93M</td>
    <td class="g">1.91M</td>
    <td class="g">2.23M</td>
  </tr>
  <tr>
    <th>Failed tool calls (FormatError)</th>
    <td class="g">0</td>
    <td class="g">0</td>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
  <tr>
    <th>Input tokens/turn (avg)</th>
    <td class="g">32,575</td>
    <td class="g">28,029</td>
    <td class="g">27,925</td>
    <td class="g">33,442</td>
  </tr>
  <tr>
    <th>Output tokens/turn (avg)</th>
    <td class="g">329</td>
    <td class="g">297</td>
    <td class="g">309</td>
    <td class="g">389</td>
  </tr>
  <tr>
    <th>Context window (peak, single turn)</th>
    <td class="g">134k</td>
    <td class="g">93k</td>
    <td class="g">117k</td>
    <td class="g">127k</td>
  </tr>
  <tr>
    <th>Wall-clock (12-way parallel)</th>
    <td class="g">3.5 h</td>
    <td class="g">2.4 h</td>
    <td class="g">2.4 h</td>
    <td class="g">2.7 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Medal tally — per instance (45 events, 4 unsolved by every model)</th>
    <th colspan="1" class="h g">Sonnet 5 — bash (control)</th>
    <th colspan="1" class="h g">Sonnet 5 — minimal prompt (pen-down fallback)</th>
    <th colspan="1" class="h g">Sonnet 5 — no ritual (pen-down only)</th>
    <th colspan="1" class="h g">Sonnet 5 — exec tool, no ritual (pen-down only)</th>
  </tr>
  <tr>
    <th rowspan="4" class="s">medals</th>
    <th>🥇 gold</th>
    <td class="g">12</td>
    <td class="g">12</td>
    <td class="g">11</td>
    <td class="g">6</td>
  </tr>
  <tr>
    <th>🥈 silver</th>
    <td class="g">8</td>
    <td class="g">7</td>
    <td class="g">15</td>
    <td class="g">8</td>
  </tr>
  <tr>
    <th>🥉 bronze</th>
    <td class="g">8</td>
    <td class="g">10</td>
    <td class="g">9</td>
    <td class="g">7</td>
  </tr>
  <tr>
    <th>placing</th>
    <td class="g">🥇 <b>1</b></td>
    <td class="g">🥈 <b>2</b></td>
    <td class="g">🥉 <b>3</b></td>
    <td class="g">4</td>
  </tr>
</tbody>
</table>

Verdicts from the pinned swebench judges. Full caveats in report.md.

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
<h3>Sonnet division — the lineage (SWE-bench Verified)</h3>
<table class="card">
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Standard — 60 <i>Python</i> events (&lt;1 h human effort)</th>
    <th colspan="1" class="h g">Claude Sonnet 4.6</th>
    <th colspan="1" class="h g">Claude Sonnet 5</th>
  </tr>
  <tr>
    <th rowspan="4" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">🥈 45</td>
    <td class="g">🥇 <b>52</b></td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥈 75%</td>
    <td class="g">🥇 <b>87%</b></td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">🥈 $35.58</td>
    <td class="g">🥇 <b>$17.34</b></td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">🥈 $0.79</td>
    <td class="g">🥇 <b>$0.33</b></td>
  </tr>
  <tr>
    <th rowspan="14" class="s t">Stats</th>
    <th class="t">Steps (total)</th>
    <td class="g t">1,953</td>
    <td class="g t">1,383</td>
  </tr>
  <tr>
    <th>Turns/instance (avg)</th>
    <td class="g">32.5</td>
    <td class="g">23.1</td>
  </tr>
  <tr>
    <th>Cost/turn (avg)</th>
    <td class="g">$0.018</td>
    <td class="g">$0.013</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">954k</td>
    <td class="g">388k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">—</td>
    <td class="g">186k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">49.81M</td>
    <td class="g">23.67M</td>
  </tr>
  <tr>
    <th>— non-cached</th>
    <td class="g">2k</td>
    <td class="g">3k</td>
  </tr>
  <tr>
    <th>— cache read</th>
    <td class="g">47.98M</td>
    <td class="g">22.39M</td>
  </tr>
  <tr>
    <th>— cache write</th>
    <td class="g">1.83M</td>
    <td class="g">1.28M</td>
  </tr>
  <tr>
    <th>Failed tool calls (FormatError)</th>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
  <tr>
    <th>Input tokens/turn (avg)</th>
    <td class="g">25,506</td>
    <td class="g">17,113</td>
  </tr>
  <tr>
    <th>Output tokens/turn (avg)</th>
    <td class="g">488</td>
    <td class="g">281</td>
  </tr>
  <tr>
    <th>Context window (peak, single turn)</th>
    <td class="g">96k</td>
    <td class="g">62k</td>
  </tr>
  <tr>
    <th>Wall-clock (12-way parallel)</th>
    <td class="g">4.9 h</td>
    <td class="g">2.0 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Hard — 45 <i>Python</i> events (1+ h human effort)</th>
    <th colspan="1" class="h g">Claude Sonnet 4.6</th>
    <th colspan="1" class="h g">Claude Sonnet 5</th>
  </tr>
  <tr>
    <th rowspan="4" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">🥈 21</td>
    <td class="g">🥇 <b>34</b></td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥈 47%</td>
    <td class="g">🥇 <b>76%</b></td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">🥈 $105.45</td>
    <td class="g">🥇 <b>$39.63</b></td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">🥈 $5.02</td>
    <td class="g">🥇 <b>$1.17</b></td>
  </tr>
  <tr>
    <th rowspan="14" class="s t">Stats</th>
    <th class="t">Steps (total)</th>
    <td class="g t">3,025</td>
    <td class="g t">2,206</td>
  </tr>
  <tr>
    <th>Turns/instance (avg)</th>
    <td class="g">67.2</td>
    <td class="g">49.0</td>
  </tr>
  <tr>
    <th>Cost/turn (avg)</th>
    <td class="g">$0.035</td>
    <td class="g">$0.018</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">2.06M</td>
    <td class="g">725k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">—</td>
    <td class="g">368k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">197.31M</td>
    <td class="g">71.86M</td>
  </tr>
  <tr>
    <th>— non-cached</th>
    <td class="g">3k</td>
    <td class="g">4k</td>
  </tr>
  <tr>
    <th>— cache read</th>
    <td class="g">192.88M</td>
    <td class="g">69.78M</td>
  </tr>
  <tr>
    <th>— cache write</th>
    <td class="g">4.43M</td>
    <td class="g">2.08M</td>
  </tr>
  <tr>
    <th>Failed tool calls (FormatError)</th>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
  <tr>
    <th>Input tokens/turn (avg)</th>
    <td class="g">65,227</td>
    <td class="g">32,575</td>
  </tr>
  <tr>
    <th>Output tokens/turn (avg)</th>
    <td class="g">682</td>
    <td class="g">329</td>
  </tr>
  <tr>
    <th>Context window (peak, single turn)</th>
    <td class="g">438k</td>
    <td class="g">134k</td>
  </tr>
  <tr>
    <th>Wall-clock (12-way parallel)</th>
    <td class="g">10.4 h</td>
    <td class="g">3.5 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Combined — 105 <i>Python</i> events</th>
    <th colspan="1" class="h g">Claude Sonnet 4.6</th>
    <th colspan="1" class="h g">Claude Sonnet 5</th>
  </tr>
  <tr>
    <th rowspan="4" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">🥈 66</td>
    <td class="g">🥇 <b>86</b></td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥈 63%</td>
    <td class="g">🥇 <b>82%</b></td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">🥈 $141.03</td>
    <td class="g">🥇 <b>$56.97</b></td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">🥈 $2.14</td>
    <td class="g">🥇 <b>$0.66</b></td>
  </tr>
  <tr>
    <th rowspan="14" class="s t">Stats</th>
    <th class="t">Steps (total)</th>
    <td class="g t">4,978</td>
    <td class="g t">3,589</td>
  </tr>
  <tr>
    <th>Turns/instance (avg)</th>
    <td class="g">47.4</td>
    <td class="g">34.2</td>
  </tr>
  <tr>
    <th>Cost/turn (avg)</th>
    <td class="g">$0.028</td>
    <td class="g">$0.016</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">3.02M</td>
    <td class="g">1.11M</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">—</td>
    <td class="g">554k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">247.13M</td>
    <td class="g">95.53M</td>
  </tr>
  <tr>
    <th>— non-cached</th>
    <td class="g">5k</td>
    <td class="g">7k</td>
  </tr>
  <tr>
    <th>— cache read</th>
    <td class="g">240.86M</td>
    <td class="g">92.16M</td>
  </tr>
  <tr>
    <th>— cache write</th>
    <td class="g">6.26M</td>
    <td class="g">3.36M</td>
  </tr>
  <tr>
    <th>Failed tool calls (FormatError)</th>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
  <tr>
    <th>Input tokens/turn (avg)</th>
    <td class="g">49,644</td>
    <td class="g">26,617</td>
  </tr>
  <tr>
    <th>Output tokens/turn (avg)</th>
    <td class="g">606</td>
    <td class="g">310</td>
  </tr>
  <tr>
    <th>Context window (peak, single turn)</th>
    <td class="g">438k</td>
    <td class="g">134k</td>
  </tr>
  <tr>
    <th>Wall-clock (12-way parallel)</th>
    <td class="g">15.2 h</td>
    <td class="g">5.5 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Medal tally — per instance (105 events, 18 unsolved by every model)</th>
    <th colspan="1" class="h g">Claude Sonnet 4.6</th>
    <th colspan="1" class="h g">Claude Sonnet 5</th>
  </tr>
  <tr>
    <th rowspan="4" class="s"></th>
    <th>🥇 gold</th>
    <td class="g">14</td>
    <td class="g">73</td>
  </tr>
  <tr>
    <th>🥈 silver</th>
    <td class="g">52</td>
    <td class="g">13</td>
  </tr>
  <tr>
    <th>🥉 bronze</th>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
  <tr>
    <th>placing</th>
    <td class="g">🥈 <b>2</b></td>
    <td class="g">🥇 <b>1</b></td>
  </tr>
</tbody>
</table>

Verdicts from the pinned swebench judges. Full caveats in report.md.

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
<h3>cpp-variation — control against variation</h3>
<table class="card">
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Claude Opus 4.8 — cpp, 20 events</th>
    <th colspan="1" class="h g">control</th>
    <th colspan="1" class="h g">variation</th>
  </tr>
  <tr>
    <th rowspan="4" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">13</td>
    <td class="g">13</td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">65%</td>
    <td class="g">65%</td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">🥇 <b>$17.32</b></td>
    <td class="g">🥈 $32.21</td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">🥇 <b>$1.33</b></td>
    <td class="g">🥈 $2.48</td>
  </tr>
  <tr>
    <th rowspan="10" class="s t">Stats</th>
    <th class="t">Empty patches</th>
    <td class="g t">0</td>
    <td class="g t">2</td>
  </tr>
  <tr>
    <th>$/instance</th>
    <td class="g">$0.87</td>
    <td class="g">$1.61</td>
  </tr>
  <tr>
    <th>Steps</th>
    <td class="g">635</td>
    <td class="g">1,152</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">260k</td>
    <td class="g">328k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">109k</td>
    <td class="g">122k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">14.32M</td>
    <td class="g">39.20M</td>
  </tr>
  <tr>
    <th>- non-cached</th>
    <td class="g">1k</td>
    <td class="g">2k</td>
  </tr>
  <tr>
    <th>- cache read</th>
    <td class="g">13.68M</td>
    <td class="g">38.43M</td>
  </tr>
  <tr>
    <th>- cache write</th>
    <td class="g">637k</td>
    <td class="g">765k</td>
  </tr>
  <tr>
    <th>Wall-clock</th>
    <td class="g">1.0 h</td>
    <td class="g">1.5 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Claude Opus 4.8 — cpp, 20 events — per instance (20 events, 7 unsolved either way)</th>
    <th colspan="1" class="h g">control</th>
    <th colspan="1" class="h g">variation</th>
  </tr>
  <tr>
    <th rowspan="3" class="s">medals</th>
    <th>🥇 gold</th>
    <td class="g">8</td>
    <td class="g">5</td>
  </tr>
  <tr>
    <th>🥈 silver</th>
    <td class="g">5</td>
    <td class="g">8</td>
  </tr>
  <tr>
    <th>🥉 bronze</th>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Claude Sonnet 5 — cpp, 20 events</th>
    <th colspan="1" class="h g">control</th>
    <th colspan="1" class="h g">variation</th>
  </tr>
  <tr>
    <th rowspan="4" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">🥈 11</td>
    <td class="g">🥇 <b>12</b></td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥈 55%</td>
    <td class="g">🥇 <b>60%</b></td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">🥇 <b>$14.91</b></td>
    <td class="g">🥈 $20.61</td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">🥇 <b>$1.36</b></td>
    <td class="g">🥈 $1.72</td>
  </tr>
  <tr>
    <th rowspan="10" class="s t">Stats</th>
    <th class="t">Empty patches</th>
    <td class="g t">0</td>
    <td class="g t">2</td>
  </tr>
  <tr>
    <th>$/instance</th>
    <td class="g">$0.75</td>
    <td class="g">$1.03</td>
  </tr>
  <tr>
    <th>Steps</th>
    <td class="g">910</td>
    <td class="g">1,356</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">244k</td>
    <td class="g">266k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">91k</td>
    <td class="g">100k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">27.74M</td>
    <td class="g">44.26M</td>
  </tr>
  <tr>
    <th>- non-cached</th>
    <td class="g">2k</td>
    <td class="g">3k</td>
  </tr>
  <tr>
    <th>- cache read</th>
    <td class="g">26.89M</td>
    <td class="g">43.29M</td>
  </tr>
  <tr>
    <th>- cache write</th>
    <td class="g">848k</td>
    <td class="g">966k</td>
  </tr>
  <tr>
    <th>Wall-clock</th>
    <td class="g">0.9 h</td>
    <td class="g">1.3 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Claude Sonnet 5 — cpp, 20 events — per instance (20 events, 8 unsolved either way)</th>
    <th colspan="1" class="h g">control</th>
    <th colspan="1" class="h g">variation</th>
  </tr>
  <tr>
    <th rowspan="3" class="s">medals</th>
    <th>🥇 gold</th>
    <td class="g">7</td>
    <td class="g">5</td>
  </tr>
  <tr>
    <th>🥈 silver</th>
    <td class="g">4</td>
    <td class="g">7</td>
  </tr>
  <tr>
    <th>🥉 bronze</th>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Claude Fable 5 — cpp, 20 events</th>
    <th colspan="1" class="h g">control</th>
    <th colspan="1" class="h g">variation</th>
  </tr>
  <tr>
    <th rowspan="4" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">14</td>
    <td class="g">14</td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">70%</td>
    <td class="g">70%</td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">🥇 <b>$30.07</b></td>
    <td class="g">🥈 $47.71</td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">🥇 <b>$2.15</b></td>
    <td class="g">🥈 $3.41</td>
  </tr>
  <tr>
    <th rowspan="10" class="s t">Stats</th>
    <th class="t">Empty patches</th>
    <td class="g t">0</td>
    <td class="g t">2</td>
  </tr>
  <tr>
    <th>$/instance</th>
    <td class="g">$1.50</td>
    <td class="g">$2.39</td>
  </tr>
  <tr>
    <th>Steps</th>
    <td class="g">503</td>
    <td class="g">967</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">244k</td>
    <td class="g">284k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">126k</td>
    <td class="g">124k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">10.82M</td>
    <td class="g">25.22M</td>
  </tr>
  <tr>
    <th>- non-cached</th>
    <td class="g">1k</td>
    <td class="g">2k</td>
  </tr>
  <tr>
    <th>- cache read</th>
    <td class="g">10.20M</td>
    <td class="g">24.50M</td>
  </tr>
  <tr>
    <th>- cache write</th>
    <td class="g">613k</td>
    <td class="g">719k</td>
  </tr>
  <tr>
    <th>Wall-clock</th>
    <td class="g">1.4 h</td>
    <td class="g">2.0 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Claude Fable 5 — cpp, 20 events — per instance (20 events, 6 unsolved either way)</th>
    <th colspan="1" class="h g">control</th>
    <th colspan="1" class="h g">variation</th>
  </tr>
  <tr>
    <th rowspan="3" class="s">medals</th>
    <th>🥇 gold</th>
    <td class="g">10</td>
    <td class="g">4</td>
  </tr>
  <tr>
    <th>🥈 silver</th>
    <td class="g">4</td>
    <td class="g">10</td>
  </tr>
  <tr>
    <th>🥉 bronze</th>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
</tbody>
</table>

Were the C++ failures the models' or the harness's? The control gave 60s and never asked for a build, so patches that did not compile reached the marker uninspected. Varies: builds required, action timeout 60s → 900s. Control: multi.

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
<h3>SWE-bench Multilingual</h3>
<table class="card">
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h"><i>Rust</i> — 7 repos (43 events)</th>
    <th colspan="1" class="h g">fable-5</th>
    <th colspan="1" class="h g">opus-4-8</th>
    <th colspan="1" class="h g">sonnet-5</th>
    <th colspan="1" class="h g">haiku-4-5</th>
  </tr>
  <tr>
    <th rowspan="11" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">🥇 <b>36</b></td>
    <td class="g">🥈 33</td>
    <td class="g">🥈 33</td>
    <td class="g">🥉 21</td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥇 <b>84%</b></td>
    <td class="g">🥈 77%</td>
    <td class="g">🥈 77%</td>
    <td class="g">🥉 49%</td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">$47.62</td>
    <td class="g">🥈 $28.22</td>
    <td class="g">🥉 $28.36</td>
    <td class="g">🥇 <b>$14.21</b></td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">🥉 $1.32</td>
    <td class="g">🥈 $0.86</td>
    <td class="g">🥈 $0.86</td>
    <td class="g">🥇 <b>$0.68</b></td>
  </tr>
  <tr>
    <th>— axum</th>
    <td class="g">7/7</td>
    <td class="g">7/7</td>
    <td class="g">6/7</td>
    <td class="g">3/7</td>
  </tr>
  <tr>
    <th>— bat</th>
    <td class="g">6/8</td>
    <td class="g">5/8</td>
    <td class="g">5/8</td>
    <td class="g">2/8</td>
  </tr>
  <tr>
    <th>— coreutils</th>
    <td class="g">3/5</td>
    <td class="g">2/5</td>
    <td class="g">2/5</td>
    <td class="g">2/5</td>
  </tr>
  <tr>
    <th>— nushell</th>
    <td class="g">5/5</td>
    <td class="g">5/5</td>
    <td class="g">5/5</td>
    <td class="g">5/5</td>
  </tr>
  <tr>
    <th>— ripgrep</th>
    <td class="g">2/2</td>
    <td class="g">2/2</td>
    <td class="g">2/2</td>
    <td class="g">2/2</td>
  </tr>
  <tr>
    <th>— ruff</th>
    <td class="g">6/7</td>
    <td class="g">5/7</td>
    <td class="g">6/7</td>
    <td class="g">2/7</td>
  </tr>
  <tr>
    <th>— tokio</th>
    <td class="g">7/9</td>
    <td class="g">7/9</td>
    <td class="g">7/9</td>
    <td class="g">5/9</td>
  </tr>
  <tr>
    <th rowspan="13" class="s t">Stats</th>
    <th class="t">Bug fixed (F2P clean)</th>
    <td class="g t">40</td>
    <td class="g t">37</td>
    <td class="g t">37</td>
    <td class="g t">26</td>
  </tr>
  <tr>
    <th>Near misses (fixed, P2P broke)</th>
    <td class="g">4</td>
    <td class="g">4</td>
    <td class="g">4</td>
    <td class="g">5</td>
  </tr>
  <tr>
    <th>Build-breakers (&gt;20% P2P broke)</th>
    <td class="g">1</td>
    <td class="g">2</td>
    <td class="g">1</td>
    <td class="g">6</td>
  </tr>
  <tr>
    <th>$/instance</th>
    <td class="g">$1.11</td>
    <td class="g">$0.66</td>
    <td class="g">$0.66</td>
    <td class="g">$0.33</td>
  </tr>
  <tr>
    <th>Empty patches</th>
    <td class="g">0</td>
    <td class="g">0</td>
    <td class="g">0</td>
    <td class="g">2</td>
  </tr>
  <tr>
    <th>Steps</th>
    <td class="g">1,101</td>
    <td class="g">1,215</td>
    <td class="g">1,860</td>
    <td class="g">3,235</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">375k</td>
    <td class="g">403k</td>
    <td class="g">483k</td>
    <td class="g">687k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">171k</td>
    <td class="g">202k</td>
    <td class="g">216k</td>
    <td class="g">0k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">17.97M</td>
    <td class="g">24.59M</td>
    <td class="g">51.77M</td>
    <td class="g">82.97M</td>
  </tr>
  <tr>
    <th>- non-cached</th>
    <td class="g">2k</td>
    <td class="g">2k</td>
    <td class="g">4k</td>
    <td class="g">492k</td>
  </tr>
  <tr>
    <th>- cache read</th>
    <td class="g">17.02M</td>
    <td class="g">23.58M</td>
    <td class="g">50.15M</td>
    <td class="g">80.71M</td>
  </tr>
  <tr>
    <th>- cache write</th>
    <td class="g">948k</td>
    <td class="g">1.02M</td>
    <td class="g">1.61M</td>
    <td class="g">1.77M</td>
  </tr>
  <tr>
    <th>Wall-clock</th>
    <td class="g">2.3 h</td>
    <td class="g">2.0 h</td>
    <td class="g">2.0 h</td>
    <td class="g">3.0 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">fmtlib/fmt — <i>C++</i> (11 events)</th>
    <th colspan="1" class="h g">fable-5</th>
    <th colspan="1" class="h g">opus-4-8</th>
    <th colspan="1" class="h g">sonnet-5</th>
    <th colspan="1" class="h g">haiku-4-5</th>
  </tr>
  <tr>
    <th rowspan="4" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">3</td>
    <td class="g">🥉 4</td>
    <td class="g">🥇 <b>6</b></td>
    <td class="g">🥈 5</td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">27%</td>
    <td class="g">🥉 36%</td>
    <td class="g">🥇 <b>55%</b></td>
    <td class="g">🥈 45%</td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">$9.80</td>
    <td class="g">🥈 $7.60</td>
    <td class="g">🥉 $8.71</td>
    <td class="g">🥇 <b>$4.69</b></td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">$3.27</td>
    <td class="g">🥉 $1.90</td>
    <td class="g">🥈 $1.45</td>
    <td class="g">🥇 <b>$0.94</b></td>
  </tr>
  <tr>
    <th rowspan="13" class="s t">Stats</th>
    <th class="t">Bug fixed (F2P clean)</th>
    <td class="g t">4</td>
    <td class="g t">4</td>
    <td class="g t">6</td>
    <td class="g t">5</td>
  </tr>
  <tr>
    <th>Near misses (fixed, P2P broke)</th>
    <td class="g">1</td>
    <td class="g">0</td>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
  <tr>
    <th>Build-breakers (&gt;20% P2P broke)</th>
    <td class="g">5</td>
    <td class="g">5</td>
    <td class="g">5</td>
    <td class="g">5</td>
  </tr>
  <tr>
    <th>$/instance</th>
    <td class="g">$0.89</td>
    <td class="g">$0.69</td>
    <td class="g">$0.79</td>
    <td class="g">$0.43</td>
  </tr>
  <tr>
    <th>Empty patches</th>
    <td class="g">0</td>
    <td class="g">0</td>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
  <tr>
    <th>Steps</th>
    <td class="g">187</td>
    <td class="g">274</td>
    <td class="g">437</td>
    <td class="g">893</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">94k</td>
    <td class="g">130k</td>
    <td class="g">125k</td>
    <td class="g">214k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">50k</td>
    <td class="g">77k</td>
    <td class="g">63k</td>
    <td class="g">0k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">2.57M</td>
    <td class="g">5.62M</td>
    <td class="g">18.04M</td>
    <td class="g">28.15M</td>
  </tr>
  <tr>
    <th>- non-cached</th>
    <td class="g">0k</td>
    <td class="g">1k</td>
    <td class="g">1k</td>
    <td class="g">147k</td>
  </tr>
  <tr>
    <th>- cache read</th>
    <td class="g">2.36M</td>
    <td class="g">5.35M</td>
    <td class="g">17.63M</td>
    <td class="g">27.42M</td>
  </tr>
  <tr>
    <th>- cache write</th>
    <td class="g">217k</td>
    <td class="g">269k</td>
    <td class="g">411k</td>
    <td class="g">583k</td>
  </tr>
  <tr>
    <th>Wall-clock</th>
    <td class="g">0.5 h</td>
    <td class="g">0.6 h</td>
    <td class="g">0.5 h</td>
    <td class="g">0.9 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h"><i>Go</i> — 5 repos (42 events)</th>
    <th colspan="1" class="h g">fable-5</th>
    <th colspan="1" class="h g">opus-4-8</th>
    <th colspan="1" class="h g">sonnet-5</th>
    <th colspan="1" class="h g">haiku-4-5</th>
  </tr>
  <tr>
    <th rowspan="9" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">🥇 <b>37</b></td>
    <td class="g">🥉 30</td>
    <td class="g">🥈 32</td>
    <td class="g">25</td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥇 <b>88%</b></td>
    <td class="g">🥉 71%</td>
    <td class="g">🥈 76%</td>
    <td class="g">60%</td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">$49.14</td>
    <td class="g">🥉 $33.22</td>
    <td class="g">🥈 $30.77</td>
    <td class="g">🥇 <b>$19.21</b></td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">$1.33</td>
    <td class="g">🥉 $1.11</td>
    <td class="g">🥈 $0.96</td>
    <td class="g">🥇 <b>$0.77</b></td>
  </tr>
  <tr>
    <th>— caddy</th>
    <td class="g">12/14</td>
    <td class="g">10/14</td>
    <td class="g">9/14</td>
    <td class="g">8/14</td>
  </tr>
  <tr>
    <th>— gin</th>
    <td class="g">8/8</td>
    <td class="g">5/8</td>
    <td class="g">5/8</td>
    <td class="g">4/8</td>
  </tr>
  <tr>
    <th>— hugo</th>
    <td class="g">7/7</td>
    <td class="g">6/7</td>
    <td class="g">7/7</td>
    <td class="g">5/7</td>
  </tr>
  <tr>
    <th>— prometheus</th>
    <td class="g">6/8</td>
    <td class="g">6/8</td>
    <td class="g">7/8</td>
    <td class="g">5/8</td>
  </tr>
  <tr>
    <th>— terraform</th>
    <td class="g">4/5</td>
    <td class="g">3/5</td>
    <td class="g">4/5</td>
    <td class="g">3/5</td>
  </tr>
  <tr>
    <th rowspan="13" class="s t">Stats</th>
    <th class="t">Bug fixed (F2P clean)</th>
    <td class="g t">38</td>
    <td class="g t">30</td>
    <td class="g t">33</td>
    <td class="g t">26</td>
  </tr>
  <tr>
    <th>Near misses (fixed, P2P broke)</th>
    <td class="g">1</td>
    <td class="g">0</td>
    <td class="g">1</td>
    <td class="g">1</td>
  </tr>
  <tr>
    <th>Build-breakers (&gt;20% P2P broke)</th>
    <td class="g">1</td>
    <td class="g">2</td>
    <td class="g">1</td>
    <td class="g">1</td>
  </tr>
  <tr>
    <th>$/instance</th>
    <td class="g">$1.17</td>
    <td class="g">$0.79</td>
    <td class="g">$0.73</td>
    <td class="g">$0.46</td>
  </tr>
  <tr>
    <th>Empty patches</th>
    <td class="g">0</td>
    <td class="g">0</td>
    <td class="g">0</td>
    <td class="g">1</td>
  </tr>
  <tr>
    <th>Steps</th>
    <td class="g">1,027</td>
    <td class="g">1,169</td>
    <td class="g">1,909</td>
    <td class="g">3,513</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">367k</td>
    <td class="g">429k</td>
    <td class="g">472k</td>
    <td class="g">777k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">152k</td>
    <td class="g">227k</td>
    <td class="g">202k</td>
    <td class="g">0k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">19.46M</td>
    <td class="g">32.86M</td>
    <td class="g">61.65M</td>
    <td class="g">119.01M</td>
  </tr>
  <tr>
    <th>- non-cached</th>
    <td class="g">2k</td>
    <td class="g">2k</td>
    <td class="g">4k</td>
    <td class="g">356k</td>
  </tr>
  <tr>
    <th>- cache read</th>
    <td class="g">18.47M</td>
    <td class="g">31.80M</td>
    <td class="g">60.15M</td>
    <td class="g">115.96M</td>
  </tr>
  <tr>
    <th>- cache write</th>
    <td class="g">983k</td>
    <td class="g">1.05M</td>
    <td class="g">1.50M</td>
    <td class="g">2.70M</td>
  </tr>
  <tr>
    <th>Wall-clock</th>
    <td class="g">2.2 h</td>
    <td class="g">2.1 h</td>
    <td class="g">1.9 h</td>
    <td class="g">8.2 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">TOTAL</th>
    <th colspan="1" class="h g">fable-5</th>
    <th colspan="1" class="h g">opus-4-8</th>
    <th colspan="1" class="h g">sonnet-5</th>
    <th colspan="1" class="h g">haiku-4-5</th>
  </tr>
  <tr>
    <th rowspan="4" class="s"></th>
    <th>Resolved</th>
    <td class="g">🥇 <b>76/96</b></td>
    <td class="g">🥉 67/96</td>
    <td class="g">🥈 71/96</td>
    <td class="g">51/96</td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥇 <b>79%</b></td>
    <td class="g">🥉 70%</td>
    <td class="g">🥈 74%</td>
    <td class="g">53%</td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">$106.56</td>
    <td class="g">🥉 $69.04</td>
    <td class="g">🥈 $67.84</td>
    <td class="g">🥇 <b>$38.10</b></td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">$1.40</td>
    <td class="g">🥉 $1.03</td>
    <td class="g">🥈 $0.96</td>
    <td class="g">🥇 <b>$0.75</b></td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Medal tally — counted in events</th>
    <th colspan="1" class="h g">fable-5</th>
    <th colspan="1" class="h g">opus-4-8</th>
    <th colspan="1" class="h g">sonnet-5</th>
    <th colspan="1" class="h g">haiku-4-5</th>
  </tr>
  <tr>
    <th rowspan="3" class="s"></th>
    <th>🥇 gold</th>
    <td class="g">2</td>
    <td class="g">0</td>
    <td class="g">1</td>
    <td class="g">0</td>
  </tr>
  <tr>
    <th>🥈 silver</th>
    <td class="g">0</td>
    <td class="g">1</td>
    <td class="g">2</td>
    <td class="g">1</td>
  </tr>
  <tr>
    <th>🥉 bronze</th>
    <td class="g">0</td>
    <td class="g">2</td>
    <td class="g">0</td>
    <td class="g">1</td>
  </tr>
</tbody>
</table>

Verdicts from the swebench judges; — means a contender has not entered or is unjudged.

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
<h3>Multi-SWE-bench</h3>
<table class="card">
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h"><i>C++</i> control (20 events)</th>
    <th colspan="1" class="h g">fable-5</th>
    <th colspan="1" class="h g">opus-5</th>
    <th colspan="1" class="h g">opus-4-8</th>
    <th colspan="1" class="h g">sonnet-5</th>
    <th colspan="1" class="h g">haiku-4-5</th>
  </tr>
  <tr>
    <th rowspan="8" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">🥇 <b>14</b></td>
    <td class="g">🥈 13</td>
    <td class="g">🥈 13</td>
    <td class="g">🥉 11</td>
    <td class="g">9</td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥇 <b>70%</b></td>
    <td class="g">🥈 65%</td>
    <td class="g">🥈 65%</td>
    <td class="g">🥉 55%</td>
    <td class="g">45%</td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">$30.07</td>
    <td class="g">$35.10</td>
    <td class="g">🥉 $17.32</td>
    <td class="g">🥈 $14.91</td>
    <td class="g">🥇 <b>$7.64</b></td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">$2.15</td>
    <td class="g">$2.70</td>
    <td class="g">🥈 $1.33</td>
    <td class="g">🥉 $1.36</td>
    <td class="g">🥇 <b>$0.85</b></td>
  </tr>
  <tr>
    <th>— Catch2</th>
    <td class="g">1/2</td>
    <td class="g">1/2</td>
    <td class="g">1/2</td>
    <td class="g">1/2</td>
    <td class="g">1/2</td>
  </tr>
  <tr>
    <th>— fmt</th>
    <td class="g">0/5</td>
    <td class="g">0/5</td>
    <td class="g">0/5</td>
    <td class="g">0/5</td>
    <td class="g">0/5</td>
  </tr>
  <tr>
    <th>— json</th>
    <td class="g">10/10</td>
    <td class="g">9/10</td>
    <td class="g">9/10</td>
    <td class="g">8/10</td>
    <td class="g">6/10</td>
  </tr>
  <tr>
    <th>— simdjson</th>
    <td class="g">3/3</td>
    <td class="g">3/3</td>
    <td class="g">3/3</td>
    <td class="g">2/3</td>
    <td class="g">2/3</td>
  </tr>
  <tr>
    <th rowspan="10" class="s t">Stats</th>
    <th class="t">Empty patches</th>
    <td class="g t">0</td>
    <td class="g t">0</td>
    <td class="g t">0</td>
    <td class="g t">0</td>
    <td class="g t">2</td>
  </tr>
  <tr>
    <th>$/instance</th>
    <td class="g">$1.50</td>
    <td class="g">$1.75</td>
    <td class="g">$0.87</td>
    <td class="g">$0.75</td>
    <td class="g">$0.38</td>
  </tr>
  <tr>
    <th>Steps</th>
    <td class="g">503</td>
    <td class="g">695</td>
    <td class="g">635</td>
    <td class="g">910</td>
    <td class="g">1,724</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">244k</td>
    <td class="g">527k</td>
    <td class="g">260k</td>
    <td class="g">244k</td>
    <td class="g">342k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">126k</td>
    <td class="g">419k</td>
    <td class="g">109k</td>
    <td class="g">91k</td>
    <td class="g">0k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">10.82M</td>
    <td class="g">21.74M</td>
    <td class="g">14.32M</td>
    <td class="g">27.74M</td>
    <td class="g">46.70M</td>
  </tr>
  <tr>
    <th>- non-cached</th>
    <td class="g">1k</td>
    <td class="g">1k</td>
    <td class="g">1k</td>
    <td class="g">2k</td>
    <td class="g">289k</td>
  </tr>
  <tr>
    <th>- cache read</th>
    <td class="g">10.20M</td>
    <td class="g">19.91M</td>
    <td class="g">13.68M</td>
    <td class="g">26.89M</td>
    <td class="g">45.55M</td>
  </tr>
  <tr>
    <th>- cache write</th>
    <td class="g">613k</td>
    <td class="g">1.83M</td>
    <td class="g">637k</td>
    <td class="g">848k</td>
    <td class="g">866k</td>
  </tr>
  <tr>
    <th>Wall-clock</th>
    <td class="g">1.4 h</td>
    <td class="g">6.9 h</td>
    <td class="g">1.0 h</td>
    <td class="g">0.9 h</td>
    <td class="g">1.7 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h"><i>Rust</i> control (20 events)</th>
    <th colspan="1" class="h g">fable-5</th>
    <th colspan="1" class="h g">opus-5</th>
    <th colspan="1" class="h g">opus-4-8</th>
    <th colspan="1" class="h g">sonnet-5</th>
    <th colspan="1" class="h g">haiku-4-5</th>
  </tr>
  <tr>
    <th rowspan="10" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">🥈 14</td>
    <td class="g">🥇 <b>15</b></td>
    <td class="g">11</td>
    <td class="g">🥉 13</td>
    <td class="g">11</td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥈 70%</td>
    <td class="g">🥇 <b>75%</b></td>
    <td class="g">55%</td>
    <td class="g">🥉 65%</td>
    <td class="g">55%</td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">$17.86</td>
    <td class="g">$18.24</td>
    <td class="g">🥉 $10.64</td>
    <td class="g">🥈 $9.46</td>
    <td class="g">🥇 <b>$5.49</b></td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">$1.28</td>
    <td class="g">$1.22</td>
    <td class="g">🥉 $0.97</td>
    <td class="g">🥈 $0.73</td>
    <td class="g">🥇 <b>$0.50</b></td>
  </tr>
  <tr>
    <th>— bat</th>
    <td class="g">0/1</td>
    <td class="g">0/1</td>
    <td class="g">0/1</td>
    <td class="g">0/1</td>
    <td class="g">0/1</td>
  </tr>
  <tr>
    <th>— clap</th>
    <td class="g">11/12</td>
    <td class="g">10/12</td>
    <td class="g">8/12</td>
    <td class="g">9/12</td>
    <td class="g">7/12</td>
  </tr>
  <tr>
    <th>— fd</th>
    <td class="g">1/1</td>
    <td class="g">1/1</td>
    <td class="g">1/1</td>
    <td class="g">1/1</td>
    <td class="g">1/1</td>
  </tr>
  <tr>
    <th>— nushell</th>
    <td class="g">1/2</td>
    <td class="g">2/2</td>
    <td class="g">1/2</td>
    <td class="g">2/2</td>
    <td class="g">1/2</td>
  </tr>
  <tr>
    <th>— rayon</th>
    <td class="g">1/1</td>
    <td class="g">1/1</td>
    <td class="g">1/1</td>
    <td class="g">1/1</td>
    <td class="g">1/1</td>
  </tr>
  <tr>
    <th>— tokio</th>
    <td class="g">0/3</td>
    <td class="g">1/3</td>
    <td class="g">0/3</td>
    <td class="g">0/3</td>
    <td class="g">1/3</td>
  </tr>
  <tr>
    <th rowspan="10" class="s t">Stats</th>
    <th class="t">Empty patches</th>
    <td class="g t">0</td>
    <td class="g t">0</td>
    <td class="g t">0</td>
    <td class="g t">0</td>
    <td class="g t">0</td>
  </tr>
  <tr>
    <th>$/instance</th>
    <td class="g">$0.89</td>
    <td class="g">$0.91</td>
    <td class="g">$0.53</td>
    <td class="g">$0.47</td>
    <td class="g">$0.27</td>
  </tr>
  <tr>
    <th>Steps</th>
    <td class="g">425</td>
    <td class="g">549</td>
    <td class="g">466</td>
    <td class="g">715</td>
    <td class="g">1,257</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">133k</td>
    <td class="g">312k</td>
    <td class="g">164k</td>
    <td class="g">159k</td>
    <td class="g">260k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">64k</td>
    <td class="g">222k</td>
    <td class="g">101k</td>
    <td class="g">85k</td>
    <td class="g">0k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">5.87M</td>
    <td class="g">11.67M</td>
    <td class="g">7.92M</td>
    <td class="g">16.27M</td>
    <td class="g">30.69M</td>
  </tr>
  <tr>
    <th>- non-cached</th>
    <td class="g">1k</td>
    <td class="g">1k</td>
    <td class="g">1k</td>
    <td class="g">1k</td>
    <td class="g">264k</td>
  </tr>
  <tr>
    <th>- cache read</th>
    <td class="g">5.41M</td>
    <td class="g">10.91M</td>
    <td class="g">7.47M</td>
    <td class="g">15.63M</td>
    <td class="g">29.65M</td>
  </tr>
  <tr>
    <th>- cache write</th>
    <td class="g">463k</td>
    <td class="g">765k</td>
    <td class="g">449k</td>
    <td class="g">634k</td>
    <td class="g">769k</td>
  </tr>
  <tr>
    <th>Wall-clock</th>
    <td class="g">1.1 h</td>
    <td class="g">2.3 h</td>
    <td class="g">0.7 h</td>
    <td class="g">0.7 h</td>
    <td class="g">1.2 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">tokio stack — <i>Rust</i> (org tokio-rs) (20 events)</th>
    <th colspan="1" class="h g">fable-5</th>
    <th colspan="1" class="h g">opus-5</th>
    <th colspan="1" class="h g">opus-4-8</th>
    <th colspan="1" class="h g">sonnet-5</th>
    <th colspan="1" class="h g">haiku-4-5</th>
  </tr>
  <tr>
    <th rowspan="6" class="s">Results</th>
    <th>Resolved</th>
    <td class="g">🥈 10</td>
    <td class="g">🥉 9</td>
    <td class="g">🥇 <b>11</b></td>
    <td class="g">🥇 <b>11</b></td>
    <td class="g">🥉 9</td>
  </tr>
  <tr>
    <th>Resolved %</th>
    <td class="g">🥈 50%</td>
    <td class="g">🥉 45%</td>
    <td class="g">🥇 <b>55%</b></td>
    <td class="g">🥇 <b>55%</b></td>
    <td class="g">🥉 45%</td>
  </tr>
  <tr>
    <th>Total cost</th>
    <td class="g">🥉 $21.64</td>
    <td class="g">$23.63</td>
    <td class="g">$22.37</td>
    <td class="g">🥈 $10.69</td>
    <td class="g">🥇 <b>$7.78</b></td>
  </tr>
  <tr>
    <th>$/resolved</th>
    <td class="g">$2.16</td>
    <td class="g">$2.63</td>
    <td class="g">🥉 $2.03</td>
    <td class="g">🥈 $0.97</td>
    <td class="g">🥇 <b>$0.86</b></td>
  </tr>
  <tr>
    <th>— tokio</th>
    <td class="g">4/10</td>
    <td class="g">2/10</td>
    <td class="g">4/10</td>
    <td class="g">4/10</td>
    <td class="g">4/10</td>
  </tr>
  <tr>
    <th>— tracing</th>
    <td class="g">6/10</td>
    <td class="g">7/10</td>
    <td class="g">7/10</td>
    <td class="g">7/10</td>
    <td class="g">5/10</td>
  </tr>
  <tr>
    <th rowspan="10" class="s t">Stats</th>
    <th class="t">Empty patches</th>
    <td class="g t">0</td>
    <td class="g t">0</td>
    <td class="g t">0</td>
    <td class="g t">0</td>
    <td class="g t">0</td>
  </tr>
  <tr>
    <th>$/instance</th>
    <td class="g">$1.08</td>
    <td class="g">$1.18</td>
    <td class="g">$1.12</td>
    <td class="g">$0.53</td>
    <td class="g">$0.39</td>
  </tr>
  <tr>
    <th>Steps</th>
    <td class="g">451</td>
    <td class="g">572</td>
    <td class="g">671</td>
    <td class="g">641</td>
    <td class="g">1,473</td>
  </tr>
  <tr>
    <th>Output tokens</th>
    <td class="g">166k</td>
    <td class="g">496k</td>
    <td class="g">308k</td>
    <td class="g">168k</td>
    <td class="g">327k</td>
  </tr>
  <tr>
    <th>Thinking (output)</th>
    <td class="g">78k</td>
    <td class="g">371k</td>
    <td class="g">179k</td>
    <td class="g">69k</td>
    <td class="g">0k</td>
  </tr>
  <tr>
    <th>Input tokens</th>
    <td class="g">7.74M</td>
    <td class="g">14.24M</td>
    <td class="g">18.97M</td>
    <td class="g">19.23M</td>
    <td class="g">47.76M</td>
  </tr>
  <tr>
    <th>- non-cached</th>
    <td class="g">1k</td>
    <td class="g">1k</td>
    <td class="g">1k</td>
    <td class="g">1k</td>
    <td class="g">254k</td>
  </tr>
  <tr>
    <th>- cache read</th>
    <td class="g">7.25M</td>
    <td class="g">13.56M</td>
    <td class="g">18.07M</td>
    <td class="g">18.54M</td>
    <td class="g">46.51M</td>
  </tr>
  <tr>
    <th>- cache write</th>
    <td class="g">486k</td>
    <td class="g">685k</td>
    <td class="g">901k</td>
    <td class="g">695k</td>
    <td class="g">994k</td>
  </tr>
  <tr>
    <th>Wall-clock</th>
    <td class="g">1.1 h</td>
    <td class="g">1.8 h</td>
    <td class="g">1.8 h</td>
    <td class="g">0.7 h</td>
    <td class="g">1.4 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">TOTAL</th>
    <th colspan="1" class="h g">fable-5</th>
    <th colspan="1" class="h g">opus-5</th>
    <th colspan="1" class="h g">opus-4-8</th>
    <th colspan="1" class="h g">sonnet-5</th>
    <th colspan="1" class="h g">haiku-4-5</th>
  </tr>
  <tr>
    <th colspan="2">Resolved</th>
    <td class="g">🥇 <b>38/60</b></td>
    <td class="g">🥈 37/60</td>
    <td class="g">🥉 35/60</td>
    <td class="g">🥉 35/60</td>
    <td class="g">29/60</td>
  </tr>
  <tr>
    <th colspan="2">Resolved %</th>
    <td class="g">🥇 <b>63%</b></td>
    <td class="g">🥈 62%</td>
    <td class="g">🥉 58%</td>
    <td class="g">🥉 58%</td>
    <td class="g">48%</td>
  </tr>
  <tr>
    <th colspan="2">Total cost</th>
    <td class="g">$69.57</td>
    <td class="g">$76.96</td>
    <td class="g">🥉 $50.33</td>
    <td class="g">🥈 $35.07</td>
    <td class="g">🥇 <b>$20.91</b></td>
  </tr>
  <tr>
    <th colspan="2">$/resolved</th>
    <td class="g">$1.83</td>
    <td class="g">$2.08</td>
    <td class="g">🥉 $1.44</td>
    <td class="g">🥈 $1.00</td>
    <td class="g">🥇 <b>$0.72</b></td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" class="h">Medal tally — counted in events</th>
    <th colspan="1" class="h g">fable-5</th>
    <th colspan="1" class="h g">opus-5</th>
    <th colspan="1" class="h g">opus-4-8</th>
    <th colspan="1" class="h g">sonnet-5</th>
    <th colspan="1" class="h g">haiku-4-5</th>
  </tr>
  <tr>
    <th colspan="2">🥇 gold</th>
    <td class="g">1</td>
    <td class="g">1</td>
    <td class="g">1</td>
    <td class="g">1</td>
    <td class="g">0</td>
  </tr>
  <tr>
    <th colspan="2">🥈 silver</th>
    <td class="g">2</td>
    <td class="g">1</td>
    <td class="g">1</td>
    <td class="g">0</td>
    <td class="g">0</td>
  </tr>
  <tr>
    <th colspan="2">🥉 bronze</th>
    <td class="g">0</td>
    <td class="g">1</td>
    <td class="g">0</td>
    <td class="g">2</td>
    <td class="g">1</td>
  </tr>
</tbody>
</table>

Verdicts from the Multi-SWE judging panel; — means a contender has not entered or is unjudged.

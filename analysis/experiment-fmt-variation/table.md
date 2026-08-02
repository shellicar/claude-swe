<h3>Experiment — fmt-variation (control: multilingual)</h3>
<table style="border-collapse:collapse">
<tbody>
  <tr>
    <th rowspan="1" colspan="2" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888">cpp — 11 events</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Claude Opus 4.8</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Claude Sonnet 5</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Claude Fable 5</th>
  </tr>
  <tr>
    <th rowspan="3" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;vertical-align:top">Resolved</th>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">control</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">4/11</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">6/11</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">3/11</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">variation</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">5/11</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">6/11</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">4/11</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">delta</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+1</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+0</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+1</td>
  </tr>
  <tr>
    <th rowspan="3" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;vertical-align:top;border-top:1px solid #888">Cost</th>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888">control</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888;border-top:1px solid #888">$7.60</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888;border-top:1px solid #888">$8.71</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888;border-top:1px solid #888">$9.80</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">variation</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$10.82</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$6.07</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$14.53</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">delta</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+$3.21</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">-$2.64</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+$4.73</td>
  </tr>
</tbody>
</table>

Were the fmtlib failures the models' or the harness's? All three contenders wrecked roughly 5 of 11 with zero build attempts under the control's 60s timeout. Varies: builds required, action timeout 60s → 900s. Control: multilingual.

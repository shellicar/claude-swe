<h3>Experiment — cpp-variation (control: multi)</h3>
<table style="border-collapse:collapse">
<tbody>
  <tr>
    <th rowspan="1" colspan="2" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888">cpp — 20 events</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Claude Opus 4.8</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Claude Sonnet 5</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Claude Fable 5</th>
  </tr>
  <tr>
    <th rowspan="3" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;vertical-align:top">Resolved</th>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">control</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">13/20</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">11/20</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">14/20</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">variation</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">13/20</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">12/20</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">14/20</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">delta</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+0</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+1</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+0</td>
  </tr>
  <tr>
    <th rowspan="3" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;vertical-align:top;border-top:1px solid #888">Cost</th>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888">control</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888;border-top:1px solid #888">$17.32</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888;border-top:1px solid #888">$14.91</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888;border-top:1px solid #888">$30.07</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">variation</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$32.21</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$20.61</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$47.71</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">delta</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+$14.89</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+$5.70</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">+$17.65</td>
  </tr>
</tbody>
</table>

Were the C++ failures the models' or the harness's? The control gave 60s and never asked for a build, so patches that did not compile reached the marker uninspected. Varies: builds required, action timeout 60s → 900s. Control: multi.

THE SIMBRIEF API

Release 1.1 - 26/08/2021
https://www.simbrief.com
contact@simbrief.com



 ** INTRODUCTION **

This ZIP archive should contain 5 files: "README.txt" describes how to implement and use the SimBrief API. It also outlines the terms of use.

Next, "demo.php" and "demo_output.php" are the PHP files which drive the API demo, which can be viewed at: https://www.simbrief.com/api/demo.php . These files are included as they represent a working implementation of the API, which you may examine should you require any clarification along the way.

Finally, "simbrief.apiv1.php" and "simbrief.apiv1.js" are the backbone of the API. They contain pre-made functions that greatly simplify adding the API to a website. However, if your specific website requires a different method and you feel you understand how these Javascript and PHP files work, you may write your own functions instead. Please contact us if you wish to do this to ensure you remain within the API's terms of use.

Every effort was made to simplify the process of adding the API to a website, however we have not included any guidelines on how to use the data output. This guide assumes at least a basic knowledge of PHP. You should know how to read and use PHP variables, in particular Objects and Arrays in order to use the data output effectively.



 ** THE GOAL **

The SimBrief API is aimed at VA creators and administrators who wish to include SimBrief flight plans on their website. When a flight plan is generated using the API, it returns an XML data file containing nearly every internal SimBrief variable which was used in the process. This provides the utmost in flexibility; users seeking a quick and easy solution might choose to simply display the OFP text and/or PDF file on their VA's dispatch page, while others may want to create an entire custom dispatch system along with a custom OFP layout. Because of the wide range of variables this API returns, the possibilities are endless.



 ** HOW IT WORKS **

First and foremost, this process does not bypass the SimBrief login system. This means that should you develop dispatch tools using the API, any pilots who wish to use them will require a SimBrief/Navigraph account. This is necessary as SimBrief must be able to track which AIRAC cycle to deliver to the user currently using your system.

The way you design your system is largely up to you, however when one of your users finally requests a flight plan (by pressing your system's "Generate" button, for example), a small popup window is created to house the SimBrief background process. If your pilot is not already logged into the SimBrief website, this popup window will ask them to enter their username and password before continuing. The popup will then display a progress bar indicating the flight plan's progress.

Once done, the popup window will automatically close and your pilot will be sent back to your VA's website, where they will be able to view their flight plan. 



 ** USING THE API **

Getting started is relatively simple, as all the required Javascript and PHP functions are included with this Readme file. The basic guidelines are as follows:

 - On the page which calls the API, you will need to include an html <form> containing the dispatch options you would like to use. The <input> names for each option are the same as those listed in the VA Integration thread, and can be viewed here: http://www.simbrief.com/forum/viewtopic.php?f=6&t=243 . Inputs not named properly will be ignored when generating the flight plan. 

 - At the very least, you must include the following inputs: 'orig', 'dest', and 'type'. Any other omitted inputs will be replaced with default values. If the 'route' input is omitted, one will be automatically selected by SimBrief.

 - You must include <script type="text/javascript" src="simbrief.apiv1.js"></script> in your html <head> tag, as it contains the necessary functions for the API to operate.

 - The <form> containing your Dispatch Options must have at least the following property: <form id="sbapiform">.

 - Your form's submit button must have at least the following property: <input type="button" onclick="simbriefsubmit('referral_page');">, where "referral_page" is the link to the page you want the API to redirect to when the flight plan is ready. This is normally your custom output page.

 - The "simbrief.apiv1.php" file will need to be included (<?php include 'simbrief.apiv1.php'; ?>) in your VA's dispatch output page. It should reside in the same directory as the rest of your dispatch system, however if you absolutely need to have it in a different directory, you will need to modify the "var api_dir =" line in the "simbrief.apiv1.js" file to point to the proper location.

 - Prior to using the API, you must obtain an API key and paste it into your "simbrief.apiv1.php" file. Failure to do this will result in your flightplan requests being denied. You should have received an API key with this package, if you did not, please contact us at contact@simbrief.com and include how you intend to use the API. 



 ** VIEW THE DEMO **

A "Demo" of the API can be viewed here: http://www.simbrief.com/api/demo.php . Please pay no attention to the page style (or lack thereof), it is merely meant to illustrate how the popup window works and what kind of information is available afterwards in the resulting XML file. It should be noted that the PHP class can also provide the data as a standard PHP array and as a JSON object.



 ** TERMS AND CONDITIONS **

Use of this API is subject to the SimBrief and Navigraph terms and conditions, available here: http://www.simbrief.com/home/index.php?page=terms

In addition, individuals wishing to use this API must have an API key assigned to them. Any attempt to circumvent the API authorization, steal another developer's API key, hack, compromise, or gain unauthorized access to the SimBrief website or it's web systems, or bypass or allow others to bypass the SimBrief.com login screen will result in immediate revocation of the associated API key, and in serious situations, legal action at our discretion. We reserve the right to revoke or block an API key at any time for any reason deemed necessary. 

The contents of the SimBrief API package are freeware, however you may not distribute this package, with or without modifications, without our prior consent in writing.
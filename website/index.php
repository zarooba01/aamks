<?php
# menu/*{{{*/
$menu=" 
<ul>
<li class='lnav'><a href=?node=about>About</a>
<li class='lnav'><a style='color: #f8f' href=?node=devel>Try out Aamks</a>
<li class='lnav'><a target=_blank href=https://www.youtube.com/channel/UCKhHI32-1TQL6AKQ4IdDRLg>Youtube</a>
<li class='lnav'><a href=?node=tests>Tests</a>
<li class='lnav'><a href=?node=papers>Papers</a>
<li class='lnav'><a target=_blank href=https://github.com/aamks/aamks>Github</a>
<li class='lnav'><a href=?node=authors>Authors</a>
<li class='lnav'><a href=?node=download>Get AAMKS on your system</a>

</ul>
";
/*}}}*/

$nodes['about']=array("About Aamks", /*{{{*/
"
Aamks is an open source, web-based platform for assessing the fire safety of humans in buildings.
Aamks runs hundreds of fire simulations (CFAST) and evacuation simulations
(Aamks.Evac) and then evaluates the results. In each simulation humans
are moving across the building and are affected by fire and smoke.<br><br>

Aamks is an open source software released under the GPL license.

");
/*}}}*/
$nodes['devel']=array("Development version", /*{{{*/
"
Here you can play with the up-to-date (but probably buggy here and there) <a href=https://student.szach.in/aamks/q.php?p=demo&s=simple&apainter=1>development version</a>.
<br><br>

Aamks is not production ready (we haven't yet released a stable version). This
server doesn't have the computing power to run simulations for you. We provide
this version so that you can get the idea what Aamks is all about.

"); /*}}}*/
$nodes['papers']=array("Publications related Aamks", /*{{{*/
"
<ol>
<li> Krasuski, A. & Pecio, M. Application of an Integrated Risk Assessment Software to Quantify the Life Safety Risk in Building during a Fire. MATEC Web Conf. 247, 00011, 1–8 (2018). <a href=https://www.matec-conferences.org/articles/matecconf/pdf/2018/106/matecconf_fese2018_00011.pdf>pdf</a>
<li> Krasuski, A. & Kuziora, Ł. Comparison of Risk Categorization Methods in a Multisimulation Framework. MATEC Web Conf. 247, 00018, 1–8 (2018). <a href=https://www.matec-conferences.org/articles/matecconf/pdf/2018/106/matecconf_fese2018_00018.pdf>pdf</a>
<li> Kreński, K. & Fliszkiewicz, M. Aamks: the platform for assessing fire safety of humans in buildings. MATEC Web Conf. (2018). doi:10.1051/matecconf/201824700001 <a href=https://www.matec-conferences.org/articles/matecconf/pdf/2018/106/matecconf_fese2018_00001.pdf>pdf</a>
<li> Kubica, P. & Wdowiak, T. The use of multisimulation in determining fire hazards in buildings covered by expertise. MATEC Web Conf. (2018). doi:10.1051/matecconf/201824700061 <a href=https://www.matec-conferences.org/articles/matecconf/pdf/2018/106/matecconf_fese2018_00061.pdf>pdf</a>
<li> Krasuski, A. Multisimulation: Stochastic simulations for the assessment of building fire safety. (The Main School of Fire Service, 2019).
<li> Krasuski, A. & Hostikka, S: Aamks – Integreated Cloud-based Application for Probabilistc Fire Risk Assessment. Proceeding of Interflam 2019 conferece
</ol>

");
/*}}}*/
$nodes['tests']=array("Tests", /*{{{*/
'
<br> Verif 1_1 <br><br>
<iframe width="560" height="315" src="https://www.youtube.com/embed/8OOwM3hcTZw" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
<br> Verif_2_1<br><br>
<iframe width="560" height="315" src="https://www.youtube.com/embed/nK5QWX4otP8" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
<br> Verif_2_3<br><br>
<iframe width="560" height="315" src="https://www.youtube.com/embed/7OKO1P6Ju1A" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
<br> Verif_2_4<br><br>
<iframe width="560" height="315" src="https://www.youtube.com/embed/c714B5FAZjo" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
<br> Verif_2_5<br><br>
<iframe width="560" height="315" src="https://www.youtube.com/embed/ysjOF7TZg68" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
<br> Verif_2_6<br><br>
<iframe width="560" height="315" src="https://www.youtube.com/embed/R7rar76V5rE" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
<br> Verif_2_8<br><br>
<iframe width="560" height="315" src="https://www.youtube.com/embed/3NNIFSQXasQ?list=PLcR1x6fD9inVo59Gt3gHmy8QLRBonH-H1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
<br> Verif_3_1<br><br>
<iframe width="560" height="315" src="https://www.youtube.com/embed/6m-3JYUX3oY?list=PLcR1x6fD9inVo59Gt3gHmy8QLRBonH-H1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
<br> Real building evacuation test<br><br>
<iframe width="560" height="315" src="https://www.youtube.com/embed/X6JcT1bwU9Q?list=PLcR1x6fD9inVo59Gt3gHmy8QLRBonH-H1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
<br> Comparison of Aamks and Pathfinder evacuation modeling<br><br>
<iframe width="560" height="315" src="https://www.youtube.com/embed/S3Cwwdwgomc" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

<br><br><br><br>
<br> A <a href=http://gamma.cs.unc.edu/Menge/>Menge</a> comparison of local movement models: RVO2 vs Helbing vs Karamouzas.<br>
Aamks uses RVO2 (ORCA).<br>
Karamouzas is Predictive Collision Pedestrian Model (2009). https://doi.org/10.1007/978-3-642-10347-6_4
<br><br>

<iframe width="800" height="500" src="https://www.youtube.com/embed/7dch-dgSuqU" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe><br><br><br>
<iframe width="800" height="500" src="https://www.youtube.com/embed/rlJzKSKhhg8" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

');
/*}}}*/
$nodes['authors']=array("Authors", /*{{{*/
"
Core developers
<ul>
<li><a target=_blank href=https://github.com/akrasuski>Adam Krasuski</a>
<li><a target=_blank href=https://github.com/mimooh>Karol Kreński</a>
<li><a target=_blank href=https://github.com/fliszer>Mateusz Fliszkiewicz</a>
</ul>
Contributors
<ul>
<li>Andrzej Krauze
<li>Hubert Zawistowski
<li>Mateusz Mackiewicz
<li>Mateusz Zimny
<li>Simo Hostikka
<li>Stanisław Łazowy
<li>Wojtek Kowalski
</ul>

");
/*}}}*/
/*}}}*/
$nodes['download']=array("Get AAMKS on your system", /*{{{*/
'
<div class="content" style="margin-left: 5%; margin-bottom:20px"> 

	<article>
	<header>
	<div>
	<h1 class="h2"> Get AAMKS on your system </h1>
	</div>
	</header>
	<content>

			<div class="step">	
				<div class="h3">
					1. Install Docker
				</div>
				<div class="info">
						<p>Below instruction how to install docker on Ubuntu 20.04. If some issues appear, check <a href="https://docs.docker.com/engine/install/ubuntu/">here</a>. </p>
						<p>How to install docker on different platforms,@ check <a href="https://docs.docker.com/engine/install/">here</a>. </p>
						
						<p>Open terminal and execute commands: </p>
						<p style="font-size:small;"> <i>(always copy the text after $)</i> </p>
						<p class="code"> $ sudo apt-get update </p>
						<p class="code"> $ 	sudo apt-get install \
							apt-transport-https \
							ca-certificates \
							curl \
							gnupg \
							lsb-release </p>
						<p class="code"> $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg </p>
 						<p class="code"> $ sudo apt-get install docker-ce docker-ce-cli containerd.io </p>
 						<p> <b>Check</b> that docker works:</p>
 						<p class="code"> $ docker</p>
 						<p style="font-size:small;"> <i>(<b>Check</b> is only to test process, its not necessery to execute)</i> </p>	
 						<img src="images/docker_test.png" width=740px>

 				</div>

			</div>

			<div class="step">	
				<div class="h3">
					2. Download image 

				</div>
				<div class="info">
						<p> Download aamks image from dockerhub</p>
						<p class="code"> $ docker pull zarooba/aamksinstall:working</p>
						<p> <b>Check</b> that you have proper image downloaded:</p>
						<p class="code"> $ docker image ls</p> 
						<img src="images/image_ls.png" width=740px>


 				</div>

			</div>

			<div class="step">	
				<div class="h3">
					3. Create network 
				</div>
				<div class="info">
						<p>Create network on which aamks will serve data, if you dont want to work on localhost</p>
						<p class="code"> $ docker network create --subnet=192.168.0.0/16 net_aamks</p>
						<p> <b>Check</b> that the network exists: </p>
 						<p class="code"> docker network ls</p>
 						<img src="images/networks.png" width=740px>


 				</div>

			</div>

			<div class="step">	
				<div class="h3">
					4. Run container
				</div>
				<div class="info">
						<p> Run container based on aamks image </p>
						<p class="code"> $ docker run -it --network=net_aamks zarooba/aamksinstall:working </p>
 						<p> Running container is shown in last line: root@------------:/usr/local#. The rest of commands should be executed in container.</p>
						<img src="images/docker_run.png" width=740px>
 				</div>

			</div>

			<div class="step">	
				<div class="h3">
					5. Restart apache and postgres
				</div>
				<div class="info">
						<p> Apache2 and Postgresql have to be restarted to work properly</p>
						<p> Restart these services in working container (root@------------:/usr/local#) </p>
						<p class="code"> $ service apache2 restart</p>
 						<p class="code"> $ service postgresql restart</p>
 						<img src="images/restart.png" width=740px>
 						<p></p>
 						<p> During restarting apache2 you will see message: </p>
 						<p class="code"> <i>AH00558: apache2: Could not reliably determine the servers fully qualified domain name, using <b>170.0.0.2.</b> Set the 'ServerName' directive globally to suppress this message </i></p>
 						<p> IP that appears in message (in this case <b>170.0.0.2</b>) is the IP that has to be written in your browser (google chrome). By this IP your browser will connect with AAMKS.

 

 				</div>

			</div>

			<div class="step">	
				<div class="h3">
					6. Work on your project!
				</div>
				<div class="info"">
						<p> Open google chrome on your computer. If you dont have it, download <a href ="https://www.google.com/intl/pl/chrome/">here</a> </p>
 						<p> Run <b>170.0.0.2/aamks</b> (in this case - IP from step 5.) in google chrome. You should see this:</p>
 						<img src="images/link.png" width=370px>
 						<p> AAMKS home site should be shown. Click register (under the login form) and fill register form.</p>
						<img src="images/home_site.png" width=370px>
						<p class="h4 mt-2"> Now you can work on your project!</p>
						

 				</div>

			</div>

		</content>

		</div>

	</article>

	</div>

');

#Engine/*{{{*/
if(!isset($_GET['node'])){
	$_GET['node']='about';
}
$title=$nodes[$_GET['node']][0];
$content=$nodes[$_GET['node']][1];

echo " 

<HTML>
<HEAD>
<TITLE>Aamks</TITLE>
<META http-equiv=Content-Type content='text/html; charset=utf-8' />
<LINK rel='stylesheet' type='text/css' href='css.css'>
</HEAD>

<menu>$menu</menu>
<page> <h1>$title<br><br></h1>$content</page>
<a target=_blank href=https://student.szach.in/aamks/q.php?p=demo&s=simple&apainter=1> <header><img src=logo.svg></header></a>


";
/*}}}*/

?>

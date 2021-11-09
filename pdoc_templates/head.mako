



<!DOCTYPE html>
<html lang="en">
  <head>
      
      
      <title>Label Studio — Data Labeling</title>
      
      <meta charset="utf-8">
      <meta name="description" content="Label Studio - Data labeling, annotation and exploration tool">
      <meta name="viewport" content="width=device-width, initial-scale=1">

      <meta property="og:type" content="article">
      
      <meta property="og:title" content="Label Studio">
      
      <meta property="og:description" content="Label Studio - Data labeling, annotation and exploration tool">

      <meta name="twitter:card" content="summary">
      
      <meta property="twitter:title" content="Label Studio">
      
      <meta name="twitter:description" content="Label Studio - Data labeling, annotation and exploration tool">

      
        <meta name="twitter:image" content="https://labelstud.io/images/opossum/heartex_icon_opossum_green@2x.png"/>
        <meta name="thumbnail" content="https://labelstud.io/images/opossum/heartex_icon_opossum_green@2x.png"/>
        <meta property="og:image" content="https://repository-images.githubusercontent.com/192640529/6b34d180-dd95-11e9-8016-fddd7751cb2c" />
            
      
      <meta name="msapplication-TileColor" content="#4fc08d">
      <meta name="theme-color" content="#4fc08d">

      <link rel="shortcut icon" type="image/x-icon" href="/images/favicon.ico"/>

      <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800&display=swap" rel="stylesheet">
    
      <link href='//fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,600|Roboto Mono' rel='stylesheet' type='text/css'>
      <link href='//fonts.googleapis.com/css?family=Dosis:500&text=LabelStudio' rel='stylesheet' type='text/css'>
      <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet" type="text/css">
    

      <!-- Place this tag in your head or just before your close body tag. -->
      <script src="/js/redirects.js"></script>
      <script src="/js/jquery.min.js"></script>
      <script async defer src="https://buttons.github.io/buttons.js"></script>
      <script src="/js/search.js"></script>
      <script src="/js/highlightjs-badge.min.js"></script>
      <script src="/js/smooth-scroll.min.js"></script>

      
<link rel="stylesheet" href="/css/new-styles.css">

      
<link rel="stylesheet" href="/css/search.css">


    <!-- main page styles -->
    
      
<link rel="stylesheet" href="/css/page.css">

    

    

    <!-- this needs to be loaded before guide's inline scripts -->

    
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-129877673-4"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-129877673-4');
</script>

<script> (function(){ window.ldfdr = window.ldfdr || {}; (function(d, s, ss, fs){ fs = d.getElementsByTagName(s)[0]; function ce(src){ var cs = d.createElement(s); cs.src = src; setTimeout(function(){fs.parentNode.insertBefore(cs,fs)}, 1); } ce(ss); })(document, 'script', 'https://sc.lfeeder.com/lftracker_v1_lYNOR8xWxQQaWQJZ.js'); })(); </script>


    <!-- docsearch -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/docsearch.js@2/dist/cdn/docsearch.min.css" />
  <meta name="generator" content="Hexo 5.4.0"></head>
  <body >
    <div id="mobile-bar" >
        <a class="menu-button"></a>
    </div>

    <header>
  <div class="container">
    <div class="outer__header">
      <div class="left__header">
        <a href="/">
          <img src="/images/new/htx_white.svg" alt="logo">
        </a>
      </div>
      <a target="_blank" rel="noopener" href="https://heartex.com/company/introducing-heartex-label-studio-teams" class="new-product-link">Label Studio Teams Edition</a>
      <a class="join__slack" target="_blank" href="http://slack.labelstud.io.s3-website-us-east-1.amazonaws.com?source=site-header">
        <img src="/images/new/logoslack.svg" alt="logoslack" />
        Join Community
      </a>
    </div>
  </div>
</header>


    
      
<link rel="stylesheet" href="/css/new-header.css">


<div class="head__main">
  <div class="small__head">
    <a href="/">
      <img src="/images/new/logofirst.svg" alt="logofirst">
    </a>
    <div class="menu__icon">
      <a>
        <span></span>
        <span></span>
        <span></span>
      </a>
    </div>
  </div>
  <div class="container__head">
    <a href="/">
      <img src="/images/new/logofirst.svg" alt="logofirst">
    </a>
    <div class="head__menu--wrapper">
      <a href="/blog" class="head-main-menu-item-link-single ">Blog</a>
      <div data-hover="true" data-delay="0" class="head-main-menu-dd w-dropdown">
        <div class="head-main-menu-dd-toggle w-dropdown-toggle" aria-controls="w-dropdown-list-0" aria-haspopup="menu" aria-expanded="false" role="button">
          <a href="/community" class="head-main-menu-item-link">Community</a>
          <svg class="head-main-menu-dd-icon w-icon-dropdown-toggle" aria-hidden="true" viewBox="0 0 16 16" stroke="#222" width="16">
            <path d="M2,6L8,12L14,6" stroke-width="2.2" fill="none"/>
          </svg>
        </div>
        <nav class="head-main-menu-dd-list w-dropdown-list">
          <a href="/community/webinars" class="w-dropdown-link">Webinars</a>
          <a href="/community/slack" class="w-dropdown-link">Slack Community</a>
          <a href="/community/newsletter" class="w-dropdown-link">Newsletter</a>
          <a href="/community/champions" class="w-dropdown-link">Champions</a>
        </nav>
      </div>
      <div data-hover="true" data-delay="0" class="head-main-menu-dd w-dropdown" style="">
        <div class="head-main-menu-dd-toggle w-dropdown-toggle" aria-controls="w-dropdown-list-1" aria-haspopup="menu" aria-expanded="false" role="button">
          <a href="/guide" class="">Documentation</a>
          <svg class="head-main-menu-dd-icon w-icon-dropdown-toggle" aria-hidden="true" viewBox="0 0 16 16" stroke="#222" width="16">
            <path d="M2,6L8,12L14,6" stroke-width="2.2" fill="none"/>
          </svg>
        </div>
        <nav class="head-main-menu-dd-list w-dropdown-list">
          <a href="/guide/index.html" class="w-dropdown-link">Quickstart</a>
          <a href="/guide/install.html" class="w-dropdown-link">Install</a>
          <a href="/guide/tasks.html" class="w-dropdown-link">Import Data</a>
          <a href="/api" class="w-dropdown-link">API Reference</a>
          <a href="/tags" class="w-dropdown-link ">Customizable Tags</a>
          <a href="/templates" class="w-dropdown-link ">Labeling Templates</a>
        </nav>
      </div>
      <a href="/playground" class="head-main-menu-item-link-single ">Playground</a>

      <br><br>
      <div class="search__head">
        <input type="text" placeholder="Search" id="docsearch-input">
        <input type="submit" value="">
      </div>

    </div>

    <!-- Place this tag where you want the button to render. -->
    <a class="github-button" target="_blank" rel="noopener" href="https://github.com/heartexlabs/label-studio" data-size="large" data-show-count="true" aria-label="Star heartexlabs/label-studio on GitHub">GitHub</a>
  </div>
  <script>

  document.querySelector(".menu__icon>a").addEventListener("click", function(e){
    e.preventDefault();
    if (document.querySelector(".menu__icon>a").classList.contains("active__menu")) {
      document.querySelector(".menu__icon>a").classList.remove("active__menu");
      document.querySelector(".container__head").style.top = "-100vh";
      document.querySelector("body , html").style.overflow = "auto";
    } else {
      document.querySelector(".menu__icon>a").classList.add("active__menu");
      document.querySelector(".container__head").style.top = "0px";
      document.querySelector("body , html").style.overflow = "hidden";
    }
  });

  document.addEventListener("DOMContentLoaded", function(event) {
      function doSomething(scroll_pos) {
          if (window.scrollY > 70) {
            document.querySelector(".head__main").classList.add("active__head");
            //document.querySelector("body").css("overflow", "hidden");
          } else {
            document.querySelector(".head__main").classList.remove("active__head");
          }
      }
      document.addEventListener('scroll', function(e) {
        doSomething();
      });
    });

    $(document).bind('keydown',function(e){
      console.log(e)
      if (document.activeElement.localName === 'body'
          && e.code !== "Space"
          && !e.altKey && !e.shiftKey && !e.ctrlKey
      ) {
        $('#docsearch-input').focus();
        $(document).unbind('keydown');
      }
    });
  </script>
</div>




      <div id="main" class="fix-sidebar">
          

  <div class="sidebar">
    <ul class="main-menu">
      
<a href="/guide/" class="">Guide</a>
<a href="/tags/" class="">Tags</a>
<a href="/templates/" class="">Templates</a>
<a href="/api/" class="">API</a>
<a href="/playground/" class="">Playground</a>
<a href="/blog/" class="">Blog</a>

<!-- Github starts -->
<div style="margin: 7px 0 0 7px !important;" class="github-button-wrap">
    <a class="github-button" target="_blank" rel="noopener" href="https://github.com/heartexlabs/label-studio"
       data-icon="octicon-star"
       data-size="large" data-show-count="true" aria-label="Star heartexlabs/label-studio on GitHub"></a>
</div>

<!-- Github repo -->
<img src="/images/github-icon.png" height="25px" style="margin-left: 10px; cursor:pointer" class="github-link"
     onclick="window.location='https://github.com/heartexlabs/label-studio'">


    </ul>
  </div>

<div class="content   ">

  
  

  <!--Add previous and next page constructors to guide pages-->
  
  

<!--content for all the website pages-->

</div>

<div class="sub-toc"></div>

      </div>

      <script src="/js/css.escape.js"></script>
      <script src="/js/common.js"></script>
    

  <script>
    // add HighlightJS-badge (options are optional)
    var options = {  // optional

       // CSS class(es) used to render the copy icon.
       copyIconClass: "fa fa-copy",
       // CSS class(es) used to render the done icon.
       checkIconClass: "fa fa-check"
    };
    window.highlightJsBadge(options);

    $(function() {
      $('.code-badge-language').each(function (o, v) {
        console.log(o)
        if ($(v).html() === 'undefined')
          $(v).html('')
        if ($(v).html() === 'bash')
          $(v).html('shell')
        if ($(v).html() === 'html')
          $(v).html('xml')
      })
    });
  </script>

  <!-- docsearch -->
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/docsearch.js@2/dist/cdn/docsearch.min.js"></script>
  <script type="text/javascript"> docsearch({
    apiKey: 'e5286d9454e04e9d10c9e927b4a4a205',
    indexName: 'labelstud',
    inputSelector: '#docsearch-input',
    debug: false // Set debug to true if you want to inspect the dropdown
    });
  </script>

  </body>
</html>

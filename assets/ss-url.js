/* Library Tabs v2 prototype: filters in the URL (?aud=…&country=…&q=…), carried between Library / Tenders / Map.
   Without JS nothing happens: tab links stay plain, every page shows everything (as live). */
(function(){
  if(!window.URLSearchParams||!history.replaceState)return;
  var P=new URLSearchParams(location.search);
  function list(k){return (P.get(k)||"").split(",").map(function(s){return s.trim();}).filter(Boolean);}
  var want={aud:list("aud"),country:list("country"),q:P.get("q")||""};
  function audBtns(){return [].slice.call(document.querySelectorAll("#audience-bar .audchip[data-v], #audrow button[data-v]"));}
  function ctyBtns(){return [].slice.call(document.querySelectorAll('.chip[data-g="country"][data-v], #ctys button[data-c]'));}
  function ctyVal(b){return b.getAttribute("data-v")||b.getAttribute("data-c");}
  function ctyOn(b){return b.getAttribute("aria-pressed")==="true"||b.classList.contains("on");}
  function read(){
    var aud=audBtns().filter(function(b){return b.getAttribute("aria-pressed")==="true";}).map(function(b){return b.getAttribute("data-v");});
    var cty=ctyBtns().filter(function(b){return ctyVal(b)!=="*"&&ctyOn(b);}).map(ctyVal);
    var qi=document.getElementById("ss-q");
    // keep values this page cannot show (e.g. country on Library) so they survive the round trip
    if(!ctyBtns().length)cty=want.country;
    return {aud:aud,country:cty,q:qi?qi.value.trim():want.q};
  }
  function qs(st,withQ){var u=new URLSearchParams();if(st.aud.length)u.set("aud",st.aud.join(","));if(st.country.length)u.set("country",st.country.join(","));if(withQ&&st.q)u.set("q",st.q);return u.toString();}
  function sync(){
    var st=read(),own=qs(st,true),carry=qs(st,false);
    history.replaceState(null,"",location.pathname+(own?"?"+own:"")+location.hash);
    [].forEach.call(document.querySelectorAll("a[data-carry]"),function(a){a.href=a.getAttribute("data-carry")+(carry?"?"+carry:"");});
  }
  function apply(){
    audBtns().forEach(function(b){if(want.aud.indexOf(b.getAttribute("data-v"))>=0&&b.getAttribute("aria-pressed")!=="true")b.click();});
    var cb=ctyBtns();
    if(want.country.length&&cb.length){
      var isMap=!!document.getElementById("ctys");
      want.country.forEach(function(c,i){if(isMap&&i>0)return;cb.forEach(function(b){if(ctyVal(b)===c&&!ctyOn(b))b.click();});});
    }
    var qi=document.getElementById("ss-q");if(qi&&want.q){qi.value=want.q;qi.dispatchEvent(new Event("input"));}
    sync();
  }
  document.addEventListener("click",function(){setTimeout(sync,0);});
  document.addEventListener("input",function(e){if(e.target&&e.target.id==="ss-q")sync();});
  if(document.readyState==="complete")setTimeout(apply,50);else addEventListener("load",function(){setTimeout(apply,50);});
})();

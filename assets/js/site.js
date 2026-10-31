// Shared rendering for the home page: price snapshot, LCOH chart, market table, news preview.
(function(){
  function fmtDelta(d, direction){
    if(direction === 'flat' || !d) return '— flat vs last week';
    var arrow = direction === 'up' ? '▲' : '▼';
    return arrow + ' ' + Math.abs(d).toFixed(2);
  }

  function renderSnapshot(data){
    var el = document.getElementById('snapshot');
    if(!el || !data) return;
    var order = ['grey','blue','green'];
    var colorVar = {grey:'var(--series-grey)', blue:'var(--series-blue)', green:'var(--series-aqua)'};
    el.innerHTML = order.map(function(key){
      var d = data[key];
      if(!d) return '';
      var deltaClass = d.direction === 'up' ? 'up' : (d.direction === 'down' ? 'down' : '');
      return '<div class="card">' +
        '<div class="label"><span class="dot" style="background:' + colorVar[key] + '"></span>' + d.label + '</div>' +
        '<div class="price">' + (d.unit && d.unit.indexOf('$') === 0 ? '$' : '') + d.price.toFixed(2) + '<span style="font-size:14px;color:var(--muted);">/kg</span></div>' +
        '<div class="delta ' + deltaClass + '">' + fmtDelta(d.delta, d.direction) + (d.note ? ' — ' + d.note : '') + '</div>' +
        '</div>';
    }).join('');
  }

  function renderChart(data){
    var svg = document.getElementById('lcoh-chart');
    if(!svg || !data) return;
    var years = data.years, series = data.series;
    var n = years.length;
    var left = 60, right = 680, top = 20, bottom = 260;
    var minV = 1.5, maxV = 6.0;
    function x(i){ return left + (right-left) * i / (n-1); }
    function y(v){ return top + (maxV - v) / (maxV - minV) * (bottom-top); }

    var gridHtml = '', labelHtml = '';
    [2,3,4,5,6].forEach(function(v){
      var yy = y(v);
      gridHtml += '<line class="gridline" x1="'+left+'" y1="'+yy+'" x2="'+right+'" y2="'+yy+'"></line>';
      labelHtml += '<text class="axislabel" x="'+(left-8)+'" y="'+(yy+3)+'" text-anchor="end">$'+v+'</text>';
    });

    function poly(key){
      return series[key].map(function(v,i){ return x(i).toFixed(1)+','+y(v).toFixed(1); }).join(' ');
    }

    var colorVar = {green:'var(--series-aqua)', blue:'var(--series-blue)', grey:'var(--series-grey)'};
    var lines = ['green','blue','grey'].map(function(key){
      return '<polyline fill="none" stroke="'+colorVar[key]+'" stroke-width="2.5" stroke-linecap="round" points="'+poly(key)+'"></polyline>';
    }).join('');

    var endLabels = ['green','blue','grey'].map(function(key){
      var vals = series[key];
      var lastV = vals[vals.length-1];
      return '<text class="endlabel" x="'+(right+6)+'" y="'+(y(lastV)+4).toFixed(1)+'" fill="'+colorVar[key]+'">$'+lastV.toFixed(2)+'</text>';
    }).join('');

    var yearLabels = years.map(function(yr,i){
      return '<text x="'+x(i).toFixed(1)+'" y="288">'+yr+'</text>';
    }).join('');

    svg.innerHTML =
      gridHtml + labelHtml + lines + endLabels +
      '<g class="axislabel" text-anchor="middle">' + yearLabels + '</g>' +
      '<line class="hoverline" id="hoverline" x1="'+left+'" y1="10" x2="'+left+'" y2="265"></line>' +
      '<g id="hitcols"></g>';

    var hitcols = document.getElementById('hitcols');
    var hoverline = document.getElementById('hoverline');
    var tooltip = document.getElementById('tooltip');
    var wrap = svg.closest('.chart-wrap');

    for(var i=0;i<n;i++){
      (function(i){
        var l = i===0 ? left-40 : (x(i-1)+x(i))/2;
        var r = i===n-1 ? right+40 : (x(i)+x(i+1))/2;
        var rect = document.createElementNS('http://www.w3.org/2000/svg','rect');
        rect.setAttribute('x', l); rect.setAttribute('y', 10);
        rect.setAttribute('width', r-l); rect.setAttribute('height', 255);
        rect.setAttribute('class','hitcol');
        rect.addEventListener('mouseenter', function(){
          hoverline.setAttribute('x1', x(i)); hoverline.setAttribute('x2', x(i));
          hoverline.style.opacity = 1;
          tooltip.innerHTML =
            '<div style="font-weight:600;margin-bottom:4px;">'+years[i]+'</div>' +
            ['green','blue','grey'].map(function(key){
              var label = key.charAt(0).toUpperCase()+key.slice(1);
              return '<div class="row"><span>'+label+'</span><span>$'+series[key][i].toFixed(2)+'</span></div>';
            }).join('');
          var ctm = svg.getScreenCTM();
          if(ctm && wrap){
            var pt = svg.createSVGPoint(); pt.x = x(i); pt.y = 0;
            var screenX = pt.matrixTransform(ctm).x;
            var wrapRect = wrap.getBoundingClientRect();
            tooltip.style.left = (screenX - wrapRect.left) + 'px';
            tooltip.style.top = '4px';
          }
          tooltip.style.opacity = 1;
        });
        rect.addEventListener('mouseleave', function(){
          hoverline.style.opacity = 0; tooltip.style.opacity = 0;
        });
        hitcols.appendChild(rect);
      })(i);
    }
  }

  function renderMarketTable(data){
    var el = document.getElementById('market-table-body');
    if(!el || !data) return;
    var pillClass = {grey:'pill-grey', blue:'pill-blue', green:'pill-green'};
    el.innerHTML = data.rows.map(function(r){
      var label = r.pathway.charAt(0).toUpperCase()+r.pathway.slice(1);
      return '<tr><td>'+r.market+'</td><td><span class="typepill '+pillClass[r.pathway]+'">'+label+'</span></td><td>'+r.source+'</td><td class="num">'+r.price+'</td></tr>';
    }).join('');
    var fn = document.getElementById('market-footnote');
    if(fn && data.footnote) fn.textContent = data.footnote;
  }

  function renderNews(data, opts){
    opts = opts || {};
    var limit = opts.limit;
    var el = document.getElementById(opts.targetId || 'news-grid');
    if(!el) return;
    if(!data || !data.items || data.items.length === 0){
      el.innerHTML = '<p style="color:var(--muted);padding:16px 2px;">No headlines yet — run <code>scripts/news_scraper.py</code> to populate this feed.</p>';
      return;
    }
    var items = limit ? data.items.slice(0, limit) : data.items;
    el.innerHTML = items.map(function(it){
      return '<div class="newsitem">' +
        '<div class="cat">'+(it.category || 'News')+'</div>' +
        '<h3><a href="'+it.url+'" target="_blank" rel="noopener">'+it.title+'</a></h3>' +
        '<div class="meta">'+it.source+' · '+it.date+'</div>' +
        '</div>';
    }).join('');
  }

  window.HPW = {
    loadJSON: function(path){ return fetch(path).then(function(r){ return r.json(); }); },
    renderSnapshot: renderSnapshot,
    renderChart: renderChart,
    renderMarketTable: renderMarketTable,
    renderNews: renderNews
  };
})();

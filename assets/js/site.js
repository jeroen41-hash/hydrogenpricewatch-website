// Shared rendering for the home page: price snapshot, LCOH chart, market table, news preview.
(function(){
  function renderSnapshot(data){
    var el = document.getElementById('snapshot');
    if(!el || !data) return;
    var order = ['grey','blue','green'];
    var colorVar = {grey:'var(--series-grey)', blue:'var(--series-blue)', green:'var(--series-aqua)'};
    el.innerHTML = order.map(function(key){
      var d = data[key];
      if(!d) return '';
      var priceHtml, noteHtml;
      if(d.kind === 'live'){
        priceHtml = '€' + d.price.toFixed(2) + '<span style="font-size:14px;color:var(--muted);">/kg</span>';
        noteHtml = '<span class="sample-tag" style="font-size:10px;">live</span> ' + d.source + ' · ' + d.as_of;
      } else {
        priceHtml = '€' + d.min.toFixed(2) + '–' + d.max.toFixed(2) + '<span style="font-size:14px;color:var(--muted);">/kg</span>';
        noteHtml = '<span class="sample-tag" style="font-size:10px;">' + d.year + ' benchmark</span> ' + d.source;
      }
      return '<div class="card">' +
        '<div class="label"><span class="dot" style="background:' + colorVar[key] + '"></span>' + d.label + '</div>' +
        '<div class="price">' + priceHtml + '</div>' +
        '<div class="delta">' + noteHtml + '</div>' +
        '</div>';
    }).join('');
  }

  function renderChart(data){
    var svg = document.getElementById('lcoh-chart');
    if(!svg || !data || !data.points) return;
    var points = data.points;
    var n = points.length;
    var left = 60, right = 680, top = 20, bottom = 260;
    var values = points.map(function(p){ return p.value; });
    var rawMin = Math.min.apply(null, values), rawMax = Math.max.apply(null, values);
    var pad = (rawMax - rawMin) * 0.15 || 1;
    var minV = Math.max(0, Math.floor(rawMin - pad)), maxV = Math.ceil(rawMax + pad);
    function x(i){ return left + (right-left) * i / (n-1); }
    function y(v){ return top + (maxV - v) / (maxV - minV) * (bottom-top); }

    var step = Math.max(1, Math.round((maxV - minV) / 5));
    var gridHtml = '', labelHtml = '';
    for(var v = minV; v <= maxV; v += step){
      var yy = y(v);
      gridHtml += '<line class="gridline" x1="'+left+'" y1="'+yy+'" x2="'+right+'" y2="'+yy+'"></line>';
      labelHtml += '<text class="axislabel" x="'+(left-8)+'" y="'+(yy+3)+'" text-anchor="end">€'+v+'</text>';
    }

    var poly = points.map(function(p,i){ return x(i).toFixed(1)+','+y(p.value).toFixed(1); }).join(' ');
    var line = '<polyline fill="none" stroke="var(--series-aqua)" stroke-width="2.5" stroke-linecap="round" points="'+poly+'"></polyline>';
    var lastP = points[points.length-1];
    var endLabel = '<text class="endlabel" x="'+(right+6)+'" y="'+(y(lastP.value)+4).toFixed(1)+'" fill="var(--series-aqua)">€'+lastP.value.toFixed(2)+'</text>';

    var xLabels = points.map(function(p,i){
      var short = p.label.replace('Calendar ', 'Cal ').replace('November', 'Nov').replace('December', 'Dec');
      return '<text x="'+x(i).toFixed(1)+'" y="288">'+short+'</text>';
    }).join('');

    svg.innerHTML =
      gridHtml + labelHtml + line + endLabel +
      '<g class="axislabel" text-anchor="middle" style="font-size:9px;">' + xLabels + '</g>' +
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
            '<div style="font-weight:600;margin-bottom:4px;">'+points[i].label+'</div>' +
            '<div class="row"><span>Green (Austria)</span><span>€'+points[i].value.toFixed(2)+'</span></div>';
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

  function renderCeghIndex(data){
    var el = document.getElementById('cegh-index');
    if(!el) return;
    if(!data || data.status !== 'ok'){
      el.innerHTML = '<p style="color:var(--muted);padding:16px 2px;">CEGH index unavailable right now — run <code>scripts/price_scraper.py</code> to refresh.</p>';
      return;
    }
    function row(item){
      return '<tr><td>'+item.label+'</td><td>'+item.delivery_period+'</td>' +
        '<td class="num">€'+item.eur_per_mwh.toFixed(2)+'</td>' +
        '<td class="num">€'+item.eur_per_kg.toFixed(2)+'</td></tr>';
    }
    var mainRows = [data.ppa100, data.ppa40, data.spot].filter(Boolean).map(row).join('');
    var forwardRows = (data.forward || []).map(function(f){
      return '<tr><td>'+f.delivery_period+'</td><td>'+f.maturity+'</td>' +
        '<td class="num">€'+f.eur_per_mwh.toFixed(2)+'</td>' +
        '<td class="num">€'+f.eur_per_kg.toFixed(2)+'</td></tr>';
    }).join('');

    el.innerHTML =
      '<p style="font-size:12.5px;color:var(--muted);margin-bottom:12px;">Published '+data.publication_date+' by CEGH · '+data.unit_basis+' · <a href="'+data.source_url+'" target="_blank" rel="noopener">source</a></p>' +
      '<div class="tablewrap"><table><thead><tr><th>Index</th><th>Delivery period</th><th style="text-align:right;">€/MWh</th><th style="text-align:right;">€/kg</th></tr></thead><tbody>'+mainRows+'</tbody></table></div>' +
      '<h3 style="font-size:14.5px;margin:20px 0 10px;font-family:var(--font-display);">Forward curve</h3>' +
      '<div class="tablewrap"><table><thead><tr><th>Delivery period</th><th>Maturity</th><th style="text-align:right;">€/MWh</th><th style="text-align:right;">€/kg</th></tr></thead><tbody>'+forwardRows+'</tbody></table></div>';
  }

  function renderIeaCosts(data){
    var el = document.getElementById('iea-costs');
    if(!el) return;
    if(!data || data.status !== 'ok'){
      el.innerHTML = '<p style="color:var(--muted);padding:16px 2px;">Benchmark unavailable right now — run <code>scripts/iea_cost_scraper.py</code> to refresh.</p>';
      return;
    }
    var pillClass = {grey:'pill-grey', blue:'pill-blue', green:'pill-green'};
    var order = ['grey','blue','green'];
    var rows = order.map(function(key){
      var p = data.pathways[key];
      if(!p || !p['2024'] || !p['2030']) return '';
      var label = key.charAt(0).toUpperCase()+key.slice(1);
      return '<tr>' +
        '<td><span class="typepill '+pillClass[key]+'">'+label+'</span></td>' +
        '<td style="color:var(--text-secondary);font-size:13px;">'+p.technologies.join(', ')+'</td>' +
        '<td class="num">€'+p['2024'].min.toFixed(2)+'–'+p['2024'].max.toFixed(2)+'</td>' +
        '<td class="num">€'+p['2030'].min.toFixed(2)+'–'+p['2030'].max.toFixed(2)+'</td>' +
        '</tr>';
    }).join('');
    el.innerHTML =
      '<div class="tablewrap"><table><thead><tr><th>Pathway</th><th>Technologies</th><th style="text-align:right;">2024 range (€/kg)</th><th style="text-align:right;">2030 projected (€/kg)</th></tr></thead><tbody>'+rows+'</tbody></table></div>' +
      '<p style="font-size:12px;color:var(--muted);margin-top:8px;">Source: '+data.source+' · <a href="'+data.source_url+'" target="_blank" rel="noopener">data</a> · '+data.note+'</p>';
  }

  window.HPW = {
    loadJSON: function(path){ return fetch(path).then(function(r){ return r.json(); }); },
    renderSnapshot: renderSnapshot,
    renderChart: renderChart,
    renderMarketTable: renderMarketTable,
    renderNews: renderNews,
    renderCeghIndex: renderCeghIndex,
    renderIeaCosts: renderIeaCosts
  };
})();

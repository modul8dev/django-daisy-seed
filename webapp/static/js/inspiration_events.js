document.addEventListener('inspiration:ready', function (e) {
  var key = e.detail && e.detail.cache_key;
  if (!key) return;

  var container = document.getElementById('inspiration-deferred');
  if (!container || container.dataset.inspirationKey !== key) return;

  var url = container.dataset.inspirationResultUrl;
  if (!url) return;

  up.render({ target: '#inspiration-deferred', url: url });
});

/* ── Compiled by Unpoly so it runs every time the fragment is inserted ── */

/* ── Add a URL image row to the formset (called from up-on-accepted) ── */
function mlAddUrlImageRow(url) {
  var container = document.querySelector('#formset-container');
  var emptyTemplate = document.querySelector('#empty-url-form');
  if (!container || !emptyTemplate) return;

  var form = container.closest('form');
  var totalInput = form.querySelector('[name$="-TOTAL_FORMS"]');
  var idx = parseInt(totalInput.value, 10);

  var clone = emptyTemplate.content.cloneNode(true);
  clone.querySelectorAll('[name], [id], [for]').forEach(function (el) {
    ['name', 'id', 'for'].forEach(function (attr) {
      var val = el.getAttribute(attr);
      if (val) el.setAttribute(attr, val.replace(/__prefix__/g, idx));
    });
  });

  var urlInput = clone.querySelector('[name$="-external_url"]');
  if (urlInput) urlInput.value = url;

  var img = clone.querySelector('.preview-img');
  var noPreview = clone.querySelector('.no-preview');
  if (img) { img.src = url; img.classList.remove('hidden'); }
  if (noPreview) noPreview.classList.add('hidden');

  container.appendChild(clone);
  totalInput.value = idx + 1;
}

up.compiler('#formset-container', function (container) {
  'use strict';

  var form = container.closest('form');
  var addBtn = form.querySelector('#add-image');
  var emptyTemplate = form.querySelector('#empty-form');

  function getTotalFormsInput() {
    return form.querySelector('[name$="-TOTAL_FORMS"]');
  }

  function getTotalForms() {
    return parseInt(getTotalFormsInput().value, 10);
  }

  function setTotalForms(val) {
    getTotalFormsInput().value = val;
  }

  /* ── Preview an image from a file input ── */
  function previewImage(input) {
    var row = input.closest('.image-row');
    if (!row) return;
    var img = row.querySelector('.preview-img');
    var noPreview = row.querySelector('.no-preview');
    if (!input.files || !input.files[0]) return;

    var reader = new FileReader();
    reader.onload = function (e) {
      img.src = e.target.result;
      img.classList.remove('hidden');
      if (noPreview) noPreview.classList.add('hidden');
    };
    reader.readAsDataURL(input.files[0]);
  }

  /* ── Add a new image row ── */
  if (addBtn && emptyTemplate) {
    addBtn.addEventListener('click', function () {
      var idx = getTotalForms();
      var clone = emptyTemplate.content.cloneNode(true);

      clone.querySelectorAll('[name], [id], [for]').forEach(function (el) {
        ['name', 'id', 'for'].forEach(function (attr) {
          var val = el.getAttribute(attr);
          if (val) {
            el.setAttribute(attr, val.replace(/__prefix__/g, idx));
          }
        });
      });

      container.appendChild(clone);
      setTotalForms(idx + 1);

      var newRow = container.lastElementChild;
      var fileInput = newRow.querySelector('input[type="file"]');
      if (fileInput) {
        var cancelHandler = function () {
          setTimeout(function () {
            if (!fileInput.files || fileInput.files.length === 0) {
              newRow.remove();
              setTotalForms(getTotalForms() - 1);
            }
          }, 300);
        };
        fileInput.addEventListener('change', function () {
          window.removeEventListener('focus', cancelHandler);
          previewImage(fileInput);
        }, { once: true });
        window.addEventListener('focus', cancelHandler, { once: true });
        fileInput.click();
      }
    });
  }

  /* ── Event delegation on the container ── */
  container.addEventListener('change', function (e) {
    if (e.target.type === 'file') {
      previewImage(e.target);
    }
  });

  container.addEventListener('click', function (e) {
    var removeBtn = e.target.closest('.remove-row');
    if (removeBtn) {
      var row = removeBtn.closest('.image-row');
      if (row) row.remove();
    }
  });

  /* ── Style delete-toggle for existing images ── */
  container.addEventListener('change', function (e) {
    var checkbox = e.target;
    if (checkbox.type !== 'checkbox') return;
    var label = checkbox.closest('.delete-toggle');
    if (!label) return;
    var row = checkbox.closest('.image-row');
    if (!row) return;

    if (checkbox.checked) {
      row.classList.add('opacity-40');
      label.classList.remove('btn-outline');
      label.querySelector('.delete-label').textContent = '↺';
    } else {
      row.classList.remove('opacity-40');
      label.classList.add('btn-outline');
      label.querySelector('.delete-label').textContent = '✕';
    }
  });

  /* ── Hide the raw checkbox inside delete-toggle labels ── */
  container.querySelectorAll('.delete-toggle input[type="checkbox"]').forEach(function (cb) {
    cb.style.position = 'absolute';
    cb.style.opacity = '0';
    cb.style.width = '0';
    cb.style.height = '0';
  });

  /* ── Paste image from clipboard ── */
  function addPastedImageRow(file) {
    if (!emptyTemplate) return;
    var idx = getTotalForms();
    var clone = emptyTemplate.content.cloneNode(true);

    clone.querySelectorAll('[name], [id], [for]').forEach(function (el) {
      ['name', 'id', 'for'].forEach(function (attr) {
        var val = el.getAttribute(attr);
        if (val) el.setAttribute(attr, val.replace(/__prefix__/g, idx));
      });
    });

    container.appendChild(clone);
    setTotalForms(idx + 1);

    var newRow = container.lastElementChild;
    var fileInput = newRow.querySelector('input[type="file"]');
    if (fileInput) {
      var dt = new DataTransfer();
      dt.items.add(file);
      fileInput.files = dt.files;
      previewImage(fileInput);
    }
  }

  function handlePaste(e) {
    if (!container.isConnected) {
      document.removeEventListener('paste', handlePaste);
      return;
    }
    var items = e.clipboardData && e.clipboardData.items;
    if (!items) return;
    for (var i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        var file = items[i].getAsFile();
        if (file) addPastedImageRow(file);
      }
    }
  }

  document.addEventListener('paste', handlePaste);

});

up.compiler('#shopify-import-form', function (form) {
  form.addEventListener('submit', function () {
    form.querySelector('#url-field').style.display = 'none';
    form.querySelector('#form-actions').style.display = 'none';
    form.querySelector('#import-spinner').style.display = 'flex';
  });
});

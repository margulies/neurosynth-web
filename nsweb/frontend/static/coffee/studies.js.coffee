# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->
  tbl=$('#studies_table').dataTable
    # "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    "sPaginationType": "full_numbers"
    "iDisplayLength": 10
    "bProcessing": true
    "bServerSide": true
    "sAjaxSource": '/api/studies/'
    "bDeferRender": true
    "bStateSave": true
  tbl.fnSetFilteringDelay(iDelay=400)

  url_id=document.URL.split('/')
  url_id=url_id[url_id.length-2]
  $('#study_features_table').dataTable
    "sPaginationType": "full_numbers"
    "iDisplayLength": 10
    "bProcessing": true
    "sAjaxSource": '/api/studies/features/'+url_id+'/'
    "bDeferRender": true
    "bStateSave": true

  $('#study_peaks_table').dataTable
    "sPaginationType": "full_numbers"
    "iDisplayLength": 10
    "bProcessing": true
    "sAjaxSource": '/api/studies/peaks/'+url_id+'/'
    "bDeferRender": true
    "bStateSave": true

    $('#study_peaks_table').on('click', 'tr', (e) =>
      row = $(e.target).closest('tr')[0]
      data = $('#study_peaks_table').dataTable().fnGetData(row)
      data = (parseInt(i) for i in data)
      viewer.moveToAtlasCoords(data)
    )
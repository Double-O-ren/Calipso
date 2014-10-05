vals = {};

setInterval(function(){
    $.ajax({
      url : '/new_data',
      dataType : 'JSON',
      async: true,
      success : function(data) {
	  if(data['new_data'])
	      updateData();
      }
    })
}, 100);


function updateData(){
    $.ajax({
      url : '/data',
      dataType : 'JSON',
      async: true,
      success : function(data) {
	  vals = $.extend(vals, data);
      }
    })
}

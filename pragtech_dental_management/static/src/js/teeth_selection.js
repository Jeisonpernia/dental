$(document).ready(function() {
var getKeySelectedArray = '';
var upkey = '';
var lowkey = '';
var status = '';

status=localStorage.getItem('status');
console.log("entering mapkeys document  ",status);
if(!status)
{
localStorage.removeItem('test');
localStorage.removeItem('upperkeys');
localStorage.removeItem('lowerkeys');
localStorage.setItem('status','0')
}


$(document).on('click', '.delete_td', function(){
      console.log('here');
      var toRemove = localStorage.getItem('toDel');
      console.log('..........to be unselected.....',toRemove)
	  image1.mapster('set', false, toRemove);
      image2.mapster('set', false, toRemove);


})

//$("input[name$='checkfield']").change(function() {alert('helooooooooo')});
//
//$("#mapchk").on('change', function() {
//    alert("triggered!");
//});



$(document).on("change", "input[type=checkbox]", function(e) {
console.log("inside checkbox fn")
var checked = $("input[type=checkbox]:checked");
var checkedValues = checked.map(function(i) { return $(this).val() }).get()
var chkstr = checkedValues.join();

getKeySelectedArray = Object.values(checkedValues);

console.log("chkkkkkkkkkkkkkkkkkkkk", chkstr,' the keys are',getKeySelectedArray, getKeySelectedArray[0])


                  _.each(getKeySelectedArray, function(sol) {
										if (sol == 'uppermouth'){
										upkey = localStorage.getItem('upperkeys');
										console.log('..........upperkeyset.....',upkey)
										image1.mapster('set', true, upkey);
										}
									});

				  _.each(getKeySelectedArray, function(sol) {
										if (sol == 'lowermouth'){
										lowkey = localStorage.getItem('lowerkeys');
										console.log('..........upperkeyset.....',lowkey)
										image2.mapster('set', true, lowkey);
										}
									});



});





           var image1 = $('#UT');
           var image2 = $('#LT');
           var image3 = $('#childUT');
           var image4 =$('#childLT');
           var options = {

            };

			default_options = {

            fillOpacity: 0.5,
            render_highlight: {
                fillColor: '2aff00',
                stroke: true,

            },
            render_select: {
                fillColor: 'ff000c',
                stroke: false,

            },

            fadeInterval: 50,
            isSelectable: true,

            mapKey: 'data-key',

            onConfigured:  function(){
            console.log("inside mapster configured fn")
            var csv = 'tooth_0,';


            var toothkey = localStorage.getItem('test');
            upkey = localStorage.getItem('upperkeys');
            lowkey = localStorage.getItem('lowerkeys');

            csv = csv+toothkey+upkey+lowkey
            console.log('the csv values configure are',csv);
            var setChk = (toothkey||upkey||lowkey);
            console.log("setChk value is",setChk)
            // the 'set' activates the areas
            if(setChk){

            image1.mapster('set', true, csv);
            image2.mapster('set', true, csv);
            }


//               document.getElementById('#showkey').value = img.mapster('get')
//               getKeySelectedArray =  getkeysFromTable();
//
//               var csv = getKeySelectedArray.toString();
//
//                // the 'set' activates the areas
//                // 'snapshot' captures the current state
//                // 'unbind(true)' disables the imagemap so users can't highlgiht & select things
//                // the 'true' parameter says "don't remove the effects, just disable it"
//
//                $('img').mapster('set',true,csv)
//                    .mapster('snapshot')
//                    .mapster('unbind',true);


                }
			};
//
          $.mapster.impl.init();
          $('#UT, #LT, #childUT, #childLT').mapster(default_options);

});
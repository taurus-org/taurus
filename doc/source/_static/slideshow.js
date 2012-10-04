$(document).ready(function() 
{	 
	var index = 0;
	var images = $("#gallery img");
	var thumbs = $("#thumbs img");
	//var imgHeight = $(thumbs).attr("height");
	//$(thumbs).slice(0,3).clone().appendTo("#thumbs");
	for (i=0; i<images.length; i++)
	{
		$(images[i]).addClass("image-"+i).hide();
	}
	
	show(index);
	setInterval(switch_image, 5000);
	
	function switch_image()
	{
		if (index<(images.length-1)){index+=1 ; }
		else {index=0}
		show (index);
	}
	
	function show(num)
	{
		$(images).fadeOut(600);
		$(".image-"+num).stop().fadeIn(600);
		console.log("Showing image " + num);
		//var scrollPos = (num+1)*imgHeight;
		//$("#thumbs").stop().animate({scrollTop: scrollPos}, 400);		
		//console.log(scrollPos, "img.image-"+num);
	}
});

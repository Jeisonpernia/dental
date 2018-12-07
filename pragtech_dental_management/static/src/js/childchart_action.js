$(document).ready(function() {
var selected_surface = new Array();
var cont = true;
var update = false;
var selected_tooth = '';
var is_tooth_select = false;

$("input[name$='chartoption']").change(function() {
    checkVal = $(this).val();
         alert(checkVal);

         if(checkVal == "adult") {
         $("div.childteethchart").hide();
         $("div.teethchartadult").show();

         }
         if(checkVal == "child"){
           $("div.teethchartadult").hide();
           $("div.childteethchart").show();

         }
$('#teethchart_child').removeClass('hidden');
$('#svg_child').removeClass('hidden');
$('#child_lowermouth').removeClass('hidden');

var svg1 = $('#svgchild1')[0];
var svg2 = $('#svg_object_child')[0];
var svg3 = $('#svgchild2')[0];
var cnt = 1;
var cnt2 = 1;
var surface2_cnt = 20;
var tooth2_cnt = 20;
for (var t = 1; t <= 20; t++) {
					var NS = 'http://www.w3.org/2000/svg';
					var svg = $('#svg_object_child')[0];

					if (cnt <= 10) {//devided teeths into 2 sections
						var path1_1 = 34.95833333333337;
						var path1_2 = 21.250000000000007;
						var path2_1 = 25.513888888888914;
						var path2_2 = 31.875000000000007;
						var path3_1 = 34.95833333333337;
						var path3_2 = 46.04166666666665;
						var path4_1 = 52.666666666666686;
						var path4_2 = 31.875000000000007;
						var path5_1 = 34.958333333333385;
						var path5_2 = 31.875000000000007;


						if (cnt == 1) {//hardcode first rectangular coordinates
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild buccal " + cnt + '_buccal 0');
							newElement.setAttribute("id", "view_" + cnt + "_top");

							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path1_1 + " " + path1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path2_1 + " " + path2_2 + ")");
							newElement.setAttribute("class", "viewchild distal " + cnt + '_distal 0');
							newElement.setAttribute("id", "view_" + cnt + "_left");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild lingual " + cnt + '_lingual 0');
							newElement.setAttribute("id", "view_" + cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path3_1 + " " + path3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild mesial " + cnt + '_mesial 0');
							newElement.setAttribute("id", "view_" + cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path4_1 + " " + path4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild occlusal " + cnt + '_occlusal 0');
							newElement.setAttribute("id", "view_" + cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path5_1 + " " + path5_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

						} else {
							var top,
							    bottom,
							    right,
							    left,
							    center;
							if (cnt <= 5) {
								top = 'buccal';
								right = 'mesial';
								bottom = 'lingual';
								left = 'distal';
								center = 'occlusal';
							} else  {
								top = 'labial';
								right = 'mesial';
								bottom = 'lingual';
								left = 'distal';
								center = 'incisal';
							}
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild " + top + " " + cnt + '_' + top + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_top");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path1_1 + (46 * (cnt - 1))) + " " + path1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild " + left + " " + cnt + '_' + left + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_left");
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path2_1 + (46 * (cnt - 1))) + " " + path2_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild " + bottom + " " + cnt + '_' + bottom + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path3_1 + (46 * (cnt - 1))) + " " + path3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild " + right + " " + cnt + '_' + right + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path4_1 + (46 * (cnt - 1))) + " " + path4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild " + center + " " + cnt + '_' + center + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path1_1 + (46 * (cnt - 1))) + " " + path4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

						}

					} else {
						var p1_1 = 33.998659373659635;
						var p1_2 = 69.01321857571864;
						var p2_1 = 24.554214929215078;
						var p2_2 = 79.63821857571861;
						var p3_1 = 33.998659373659635;
						var p3_2 = 93.80488524238524;
						var p4_1 = 51.706992706992764;
						var p4_2 = 79.63821857571861;


						if (cnt == 11) {//hardcode first rectangular coordinates
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild lingual " + surface2_cnt + '_lingual 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_top");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p1_1 + " " + p1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild distal " + surface2_cnt + '_distal 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_left");
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p2_1 + " " + p2_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild buccal " + surface2_cnt + '_buccal 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p3_1 + " " + p3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild mesial " + surface2_cnt + '_mesial 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p4_1 + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild occlusal " + surface2_cnt + '_occlusal 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p1_1 + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

						} else {
							var top,
							    bottom,
							    right,
							    left,
							    center;
							if (surface2_cnt <= 15) {
								top = 'lingual';
								right = 'mesial';
								bottom = 'labial';
								left = 'distal';
								center = 'incisal';
							} else {
								top = 'lingual';
								right = 'mesial';
								bottom = 'buccal';
								left = 'distal';
								center = 'occlusal';
							}
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild " + top + " " + surface2_cnt + "_" + top + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_top");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path1_1 + (46 * (cnt2 - 1)) - 1)) + " " + p1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild " + left + " " + surface2_cnt + "_" + left + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_left");
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path2_1 + (46 * (cnt2 - 1)) - 1)) + " " + p2_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild " + bottom + " " + surface2_cnt + "_" + bottom + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path3_1 + (46 * (cnt2 - 1)) - 1)) + " " + p3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild " + right + " " + surface2_cnt + "_" + right + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path4_1 + (46 * (cnt2 - 1)) - 1)) + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "viewchild " + center + " " + surface2_cnt + "_" + center + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path1_1 + (46 * (cnt2 - 1)) - 1)) + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);
						}

						surface2_cnt -= 1;
						tooth2_cnt -= 1;
						cnt2++;
					}
					cnt++;
				}
//svg1.append("<polyline transform="+"matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					  +" id=+"4_u_1"
//					   points="186,60,186,55,187,54,187,52,188,50,188,48,189,46,189,44,190,42,190,40,191,38,191,36,192,34,192,32,193,30,193,28,194,26,194,26,195,24,195,22,196,20,196,19,196,18,196,15,197,14,197,13,198,13,200,13,202,13,203,14,204,15,205,16,206,18,207,20,208,22,208,24,208,26,208,30,208,34,209,36,209,38,209,44,213,58,213,58,212,57,210,56,200,56,198,56,186,60"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					  +" />");
////svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="4_u_2"
//					   points="186,60,181,70,180,72,180,80,180,82,181,84,182,86,183,86,184,88,185,88,190,90,192,90,194,91,196,91,198,92,204,92,206,91,208,90,210,88,212,88,214,86,216,86,218,84,220,84,222,80,222,78,223,76,223,74,223,73,222,72,221,70,220,68,218,66,216,64,215,62,214,60,213,58,212,57,210,56,200,56,198,56,186,60"
//					   originalColor="white"
//					   style="fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   +"/>");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="5_u_1"
//					   points="243,57,243,46,244,45,244,44,245,43,245,42,246,41,246,40,247,39,247,38,247,35,247,34,246,30,245,25,244,20,245,14,248,14,250,16,252,18,254,20,255,22,256,24,257,26,258,28,259,30,260,32,261,34,262,36,263,38,264,40,265,42,265,44,265,45,266,50,267,52,268,58,268,58,267,57,266,56,265,56,264,55,263,55,262,55,260,55,258,55,250,55,243,57"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   +"/>");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="5_u_3"
//					   points="243,57,241,60,240,62,239,64,238,66,237,68,236,70,235,72,234,74,234,80,235,81,236,82,237,83,238,84,239,85,240,86,241,86,242,87,243,88,244,88,245,89,246,89,247,90,248,90,249,91,250,91,250,92,252,92,253,93,254,93,257,93,258,92,259,92,260,91,261,91,264,91,265,90,266,90,267,89,268,89,269,88,270,88,271,87,272,87,273,86,273,86,274,85,275,85,276,84,277,84,278,83,278,76,278,75,277,74,277,73,276,72,276,71,275,70,275,69,274,68,274,67,273,66,273,65,272,64,272,63,271,62,271,61,270,60,269,59,268,58,267,57,266,56,265,56,264,55,263,55,262,55,260,55,258,55,250,55,243,57"
//					   originalColor="white"
//					   style="fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   +" />");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="6_u_1"
//					   points="298,57,296,50,297,48,297,46,298,44,298,42,299,40,299,38,300,36,300,34,300,30,301,28,301,26,302,24,300,22,298,20,298,17,299,16,300,15,301,13,302,11,303,10,304,12,303,13,302,13,303,12,304,11,305,10,307,10,309,10,310,10,311,10,312,11,313,12,314,13,315,14,316,15,316,16,317,17,317,18,317,19,318,20,318,21,318,22,319,23,319,24,319,25,320,26,320,27,320,28,321,29,321,30,321,31,322,32,322,33,322,34,323,35,323,36,323,37,324,38,324,39,324,40,325,42,326,44,326,45,326,60"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   +" />");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="6_u_2"
//					   points="299,57,294,65,293,67,291,70,290,73,289,76,289,80,290,82,292,84,294,86,296,86,298,88,300,88,302,89,304,90,306,91,315,91,316,90,318,90,320,89,322,89,324,88,326,88,328,87,330,87,332,86,333,85,334,85,335,84,335,83,336,82,336,80,336,75,335,74,334,72,333,70,332,68,331,66,330,64,328,62,326,60,324,60,322,58,320,58,318,58,316,58,299,57"
//					   originalColor="white"
//					   style="fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)"+" />");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="7_u_1"
//					   points="350,60,349,50,350,48,350,46,351,44,352,42,353,40,354,38,355,36,356,34,357,32,357,31,357,30,357,28,357,26,356,20,356,16,357,14,357,12,358,11,359,11,360,11,361,11,363,12,365,13,365,14,367,15,367,16,368,18,369,20,370,22,371,24,372,26,372,28,373,30,373,32,374,34,374,36,375,38,375,40,376,42,376,44,377,48,379,60,378,58,377,58,375,57,374,56,372,55,371,54,369,54,368,53,365,54,363,54,360,55,350,60"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)" +"/>");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="7_u_2"
//					   points="350,60,346,70,345,72,344,74,344,76,344,81,345,82,346,83,347,84,348,85,349,86,350,87,352,88,354,88,356,89,358,89,360,90,370,90,380,90,382,89,384,89,386,88,388,86,388,84,388,82,388,78,387,77,387,76,387,75,386,74,386,73,385,72,384,71,384,70,383,69,383,68,382,67,382,66,381,65,381,64,380,63,380,62,379,61,379,60,378,58,377,58,375,57,374,56,372,55,371,54,369,54,368,53,365,54,363,54,360,55,350,60"
//					   originalColor="white"
//					   style="fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)"+" />");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="8_u_1"
//					   points="404,57,404,45,404,40,405,35,406,30,408,25,409,20,411,15,413,10,418,10,422,12,425,15,427,17,428,19,429,20,429,21,430,22,431,23,431,24,432,25,432,26,433,28,434,30,435,32,436,34,436,42,435,43,437,45,438,46,437,55,436,57,438,58,436,56,434,54,432,53,431,53,430,52,429,52,428,52,424,51,415,51,413,52,411,53,408,54,403,57"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)"+" />");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="8_u_2"
//					   points="403,57,399,65,398,79,399,84,400,87,402,89,435,89,436,89,440,88,444,87,445,85,445,84,445,80,445,75,444,70,443,68,442,66,441,64,440,62,439,60,438,58,436,56,434,54,432,53,431,53,430,52,429,52,428,52,424,51,415,51,413,52,411,53,408,54,403,57"
//					   originalColor="white"
//					   style="fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)"+" />");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="9_u_1"
//					   points="465,56,464,50,465,48,466,40,467,32,468,28,470,26,471,24,472,22,473,20,474,18,476,16,478,14,480,12,482,10,488,10,489,11,490,12,490,13,491,17,492,21,493,24,494,27,495,30,496,33,497,36,498,39,499,42,499,44,498,46,498,48,498,57,490,54,487,53,485,52,475,52,473,53,471,54,468,55,465,56"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)" +"/>");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="9_u_2"
//					   points="498,57,501,65,502,68,503,70,504,72,504,76,504,78,504,80,503,85,502,87,501,88,499,89,496,89,465,89,460,88,458,86,456,84,456,82,457,78,458,75,458,73,459,70,460,68,460,66,461,64,462,62,463,60,464,58,465,56,468,55,471,54,473,53,475,52,485,52,487,53,490,54,498,57"
//					   originalColor="white"
//					   style="fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)" +"/>");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="10_u_1"
//					   points="523,57,526,50,527,48,528,46,528,44,529,42,529,40,529,38,530,36,530,34,530,32,531,30,531,28,532,26,532,24,533,22,533,20,534,18,535,16,536,14,539,12,541,12,544,12,545,14,546,17,546,20,546,32,547,34,548,36,549,38,550,40,551,42,552,44,553,46,554,48,555,60,554,60,552,58,550,57,548,56,546,55,544,54,535,54,533,55,523,57"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)"+" />");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="10_u_2"
//					   points="523,57,520,65,519,67,518,69,517,71,516,73,515,75,514,85,515,88,517,89,540,89,542,88,544,88,546,87,548,87,550,86,552,86,554,85,556,84,558,82,559,80,560,78,560,76,560,74,559,72,559,70,558,68,558,66,556,64,556,62,554,60,552,58,550,57,548,56,546,55,544,54,535,54,533,55,523,57"
//					   originalColor="white"
//					   style="fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)" +"/>");
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="11_u_1"
//					   points="578,60,578,48,579,45,580,40,582,35,583,30,584,25,586,20,589,15,594,10,596,9.5,598,9.5,600,11,602,12,604,14,606,16,606,18,604,20,604,26,604,30,605,35,606,40,607,45,608,50,607,60,606,59,600,58,595,57,578,60"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)" +"/>");
//
//
//svg1.append ("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="11_u_2"
//					   points="578,60,576,62,574,64,572,66,570,68,569,70,569,72,569,80,569,81,570,82,571,84,572,86,574,87,575,87,576,88,577,88,578,89,579,89,580,90,581,90,582,90,583,91,584,91,585,91,586,92,587,92,588,92,589,92,592,92,593,91,594,91,596,91,598,90,600,90,602,89,604,88,606,86,609,84,612,82,614,80,615,79,616,75,615,73,614,70,607,60,606,59,600,58,595,57,578,60"
//					   originalColor="white"
//					   style="fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)" +"/>")
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="12_u_1"
//					   points="635,58,639,40,648,20,653,13,655,12,657,13,658,15,659,18,660,20,659,22,658,24,657,26,656,28,656,40,657,42,659,44,660,46,661,48,661,50,659,57,657,56,655,55,650,55,645,55,635,58"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)" +"/>")
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="12_u_2"
//					   points="635,58,629,68,628,70,627,72,626,74,625,76,625,78,625,81,625,83,626,84,626,85,627,86,628,87,629,88,631,89,632,90,633,90,634,90,635,91,636,91,637,91,639,91,640,92,648,92,650,91,652,91,654,90,656,89,658,88,660,86,664,84,666,82,668,80,668,79,668,73,667,71,666,69,665,67,664,65,663,63,662,61,661,59,659,57,657,56,655,55,650,55,645,55,635,58"
//					   originalColor="white"
//					   style="fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)" +"/>")
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="12_u_3"
//					   points="637,45,635,12,638,12,646,22,637,45"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)"  +"/>")
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="13_u_1"
//					   points="689,60,691,50,691,48,692,46,692,44,693,42,693,40,694,38,694,36,695,34,695,32,696,30,696,28,696,22,697,20,697,18,698,16,698,14,700,12,704,12,706,14,706,16,708,18,708,20,709,22,709,24,710,26,710,28,711,30,711,32,712,34,712,36,713,38,713,40,714,42,714,44,715,46,715,48,716,50,716,52,716,61,716,61,714,60,713,59,710,58,708,57,706,57,700,56,689,60"
//					   originalColor="yellow"
//					   style="fill:#ffff00;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)"  +"/>")
//svg1.append("<polyline
//					   transform="matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)"
//					   id="13_u_2"
//					   points="689,60,682,69,681,72,680,74,680,82,682,82,684,84,686,84,688,86,690,86,692,88,694,88,696,90,698,90,700,92,702,92,704,92,706,91,708,91,710,90,712,90,714,88,716,88,718,86,720,86,722,84,723,82,724,80,724,75,724,73,723,72,723,71,722,70,722,69,721,68,721,67,720,66,720,65,719,64,719,63,718,62,716,61,714,60,713,59,710,58,708,57,706,57,700,56,689,60"
//					   originalColor="white"
//					   style="fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3"
//					   onclick="loadToothRelatedDetails(this)" +"/>")
//
//
//	var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'polyline');
//							newElement.setAttribute("class", "viewchild root");
//							newElement.setAttribute("id", "root_1");
//							newElement.setAttribute("points", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
//							newElement.setAttribute()
//							newElement.setAttribute("transform", "matrix(0.99997296,0,0,1.0298769,-67.160563,105.53179)");
//							newElement.setAttribute("405,267,400,252,400,247,401,246,401,245,402,244,402,243,436,243,437,244,438,245,438,246,439,247,438,248,438,249,437,250,437,252,436,254,436,255,430,265,425,267,420,268,415,269,410,268,405,267")
//							newElement.setAttribute("style", "fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3");
//							svg1.appendChild(newElement);
//	var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'polyline');
//							newElement.setAttribute("class", "viewchild crown");
//							newElement.setAttribute("id", "crown_1");
//
//							newElement.setAttribute("points", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
//							newElement.setAttribute("transform", "translate(-49.9375,115.21397)");
//							newElement.setAttribute("405,267,400,252,400,247,401,246,401,245,402,244,402,243,436,243,437,244,438,245,438,246,439,247,438,248,438,249,437,250,437,252,436,254,436,255,430,265,425,267,420,268,415,269,410,268,405,267")
//							newElement.setAttribute("style", "fill:#ffffff;stroke:#000000;stroke-width:1;stroke-opacity:0.3");
//							svg1.appendChild(newElement);


//this.$el.find('#id_of_element')




    });




//
//$(document).on('click', '.viewchild', function(){
//
//
//					console.log('in click-------------')
//
////
//                    alert(this.id)
//					selected_tooth = ((this.id).split('_'))[1];
//					var svgElement = this.id;
//					console.log('the svg file is',svgElement );
//					svgElement.setAttributeNS(null, 'fill', 'purple')
//
//
//});


});
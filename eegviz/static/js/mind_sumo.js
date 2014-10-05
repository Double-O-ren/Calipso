SCORE_SCALE = 5.0;
score = 0.0;

WINDOW_SCALE = 5.0;

function initSumo(){


    renderer = new THREE.WebGLRenderer();
    renderer.setSize( window.innerWidth, window.innerHeight - 200 );
    container = renderer.domElement;
    document.body.appendChild( renderer.domElement );
    renderer.setClearColor('black',1)

    onRenderFcts	= [];
    scene	= new THREE.Scene();
    camera	= new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.01, 1000 );
    camera.position.z = 10;


    //////////////////////////////////////////////////////////////////////////////////
    //		comment								//
    //////////////////////////////////////////////////////////////////////////////////

    var dirLight = new THREE.DirectionalLight( 0xffffff, 0.125 );
    dirLight.position.set( 0, 0, 1 ).normalize();
    scene.add( dirLight );

    var pointLight = new THREE.PointLight( 0xffffff, 1.5 );
    pointLight.position.set( 0, 100, 90 );
    scene.add( pointLight );



    //////////////////////////////////////////////////////////////////////////////////
    //		Camera Controls							//
    //////////////////////////////////////////////////////////////////////////////////
/*
    var mouse	= {x : 0, y : 0}
    document.addEventListener('mousemove', function(event){
	mouse.x	= (event.clientX / window.innerWidth ) - 0.5
	mouse.y	= (event.clientY / window.innerHeight) - 0.5
    }, false)
    onRenderFcts.push(function(delta, now){
	camera.position.x += (mouse.x*20 - camera.position.x) * 0.01
	camera.position.y += (mouse.y*20 - camera.position.y) * 0.01
	camera.lookAt( scene.position )
    })

*/
    //////////////////////////////////////////////////////////////////////////////////
    //		lasers				//
    //////////////////////////////////////////////////////////////////////////////////


    laserBeamL	= new THREEx.LaserBeam(0xdd44aa)
    scene.add(laserBeamL.object3d)

    var object3d		= laserBeamL.object3d
    object3d.position.x	= -20;
    object3d.position.y	= 0;
    object3d.position.z	= 0;
    object3d.rotation.x	= 0;
    object3d.rotation.y	= 0;
    object3d.rotation.z	= 0;


    laserBeamR	= new THREEx.LaserBeam(0x1122ee)
    scene.add(laserBeamR.object3d)

    object3d		= laserBeamR.object3d
    object3d.position.x	= 20;
    object3d.position.y	= 0;
    object3d.position.z	= 0;
    object3d.rotation.x	= 0;
    object3d.rotation.y	= 0;
    object3d.rotation.z	= 0;



    //////////////////////////////////////////////////////////////////////////////////
    //		out box								//
    //////////////////////////////////////////////////////////////////////////////////
/*
	var geometry	= new THREE.CubeGeometry(1, 1, 1);
	var material	= new THREE.MeshPhongMaterial({
	    color	: 0xaa8888,
	    specular: 0xffffff,
	    shininess: 300,
	    side	: THREE.BackSide,
	});
	var object3d	= new THREE.Mesh( geometry, material )
	object3d.scale.set(10,8,10)
	scene.add(object3d)
*/

    var planeL = new THREE.Mesh(new THREE.PlaneGeometry(3, 3), new THREE.MeshNormalMaterial());
    planeL.overdraw = true;
    planeL.rotation.y = Math.PI / 2.0;
    planeL.position.x = -1.0 * WINDOW_SCALE;
    scene.add(planeL);


    var planeR = new THREE.Mesh(new THREE.PlaneGeometry(3, 3), new THREE.MeshNormalMaterial());
    planeR.overdraw = true;
    planeR.rotation.y = -1.0 * Math.PI / 2.0;
    planeR.position.x = 1.0 * WINDOW_SCALE;
    scene.add(planeR);



    //////////////////////////////////////////////////////////////////////////////////
    //		ball							//
    //////////////////////////////////////////////////////////////////////////////////

	var geometry	= new THREE.SphereGeometry(0.07, 32, 32);
	var material	= new THREE.MeshPhongMaterial({
	    color	: 0xff33dd,
	    specular: 0xdd33ff,
	    shininess: 200,
	});
	ball	= new THREE.Mesh( geometry, material )
	//object3d.position.x = 1;
	ball.scale.set(1,1,1).multiplyScalar(5)
	scene.add(ball)


    onRenderFcts.push(function(delta, now){
	updateVisualScore(5.0 * Math.sin(now));
    });

    //////////////////////////////////////////////////////////////////////////////////
    //		text							//
    //////////////////////////////////////////////////////////////////////////////////

    // add 3D text default
    var material = new THREE.MeshPhongMaterial({
        color: 0xcccccc,
	specular: 0x33dd33,
	shininess: 500,
	shading: THREE.SmoothShading,
	bevelThickness: 300,
	bevelSize: 3,
	bevelEnabled: true,
    });
    var textGeom = new THREE.TextGeometry( 'Mind Sumo', {
        font: 'helvetiker',
        size: 60
    });

    var textMesh = new THREE.Mesh( textGeom, material );

    textGeom.computeBoundingBox();
    var textWidth = textGeom.boundingBox.max.x - textGeom.boundingBox.min.x;


    textMesh.position.set( -0.5 * textWidth, 250, -1000 );
    scene.add( textMesh );


    // Do some optional calculations. This is only if you need to get the
    // width of the generated text
    textGeom.computeBoundingBox();
    textGeom.textWidth = textGeom.boundingBox.max.x - textGeom.boundingBox.min.x;

/*
    texture = THREE.ImageUtils.loadTexture("/static/images/lasers.jpg");
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;

    var plane = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshLambertMaterial({map : texture}));
    plane.overdraw = true;
    scene.add(plane);

    plane.position.z = -100;
*/


    //////////////////////////////////////////////////////////////////////////////////
    //		render the scene						//
    //////////////////////////////////////////////////////////////////////////////////
    onRenderFcts.push(function(){
	renderer.render( scene, camera );
    })

    //////////////////////////////////////////////////////////////////////////////////
    //		loop runner							//
    //////////////////////////////////////////////////////////////////////////////////
    lastTimeMsec= null
    requestAnimationFrame(function animate(nowMsec){
	// keep looping
	requestAnimationFrame( animate );
	// measure time
	lastTimeMsec	= lastTimeMsec || nowMsec-1000/60
	var deltaMsec	= Math.min(200, nowMsec - lastTimeMsec)
	lastTimeMsec	= nowMsec
	// call each update function
	onRenderFcts.forEach(function(updateFn){
	    updateFn(deltaMsec/1000, nowMsec/1000)
	})
    })



}

// val = -1..1
function updateVisualScore(){
    ball.position.x = score;
    laserBeamL.object3d.position.x = -20 + score;
    laserBeamR.object3d.position.x = 20 + score;
}

// happens every 50ms
function updateState(){
    player1_val = vals["player1_val"] || 0
    player2_val = vals["player2_val"] || 0
 //   player1_val = 2.0 * player1_val - 1.0;
 //   player2_val = 2.0 * player2_val - 1.0;
    //console.log("p1 " + player1_val.toString())
    //console.log("p2 " + player2_val.toString())
    score += SCORE_SCALE * (player2_val - player1_val) / (2.0 * WINDOW_SCALE);
    //console.log(score);
    updateVisualScore();
    check_won();
}

function check_won(){
    if(score >= WINDOW_SCALE){ // player 1 won
	clearInterval(callback);
	alert("player 1 wins!");
    }

    if(score <= -1.0 * WINDOW_SCALE){ // player 1 won
	clearInterval(callback);
	alert("player 2 wins!");
    }
}

function startSumo(){
    initSumo();
    //console.log('shiz')
    callback = setInterval(updateState, 100);
}

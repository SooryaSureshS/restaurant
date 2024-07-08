odoo.define('mask_cutomization.mask_customization', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');
publicWidget.registry.MaskCustomization = publicWidget.Widget.extend({
    selector: '#product_detail',
    events: {
//        'input #player_kit': '_player_kit',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("****************************8")
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        const canvas = document.querySelector("#three_js_container");
//        self.scene = new THREE.Scene();
//        self.scene.background = new THREE.Color( 0xffffff );
//        self.ambientLight = new THREE.AmbientLight( 0x606060 );
//            self.scene.add( self.ambientLight );
//
//            self.directionalLight = new THREE.DirectionalLight( 0xffffff );
//            self.directionalLight.position.set( 1, 0.75, 0.1 ).normalize();
//            self.scene.add( self.directionalLight );
//
//        const renderer = new THREE.WebGLRenderer();
//        renderer.setSize( window.innerWidth, window.innerHeight );


var scene = new THREE.Scene();
//scene.background = new THREE.Color( 0xDEDCDC  );
scene.background = new THREE.Color("#2f2f2f");
			var camera = new THREE.PerspectiveCamera( 2, window.innerWidth / window.innerHeight, .9, 1000 );
//			var camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
//			camera.rotation.y = 45/180*Math.PI;
//			camera.rotation.x = 800;
//			camera.rotation.y = 100;
//			camera.rotation.z = 1000;


//var camera = new THREE.PerspectiveCamera(
//	45,
//	canvas.clientWidth / canvas.clientHeight,
//	0.1,
//	100
//);
camera.position.set(0, 0, 15);

			var renderer = new THREE.WebGLRenderer();
//			renderer.setSize( window.innerWidth, window.innerHeight );
			renderer.setSize( 400, 300 );
//			document.body.appendChild( renderer.domElement );
            self.controls = new THREE.OrbitControls( camera , renderer.domElement);
//            self.controls.addEventListener('change', renderer);
            self.controls.update();
            $("#three_js_container").append(renderer.domElement);

            var hlight = new THREE.DirectionalLight(0x404040, 10)
            scene.add(hlight)

//            var dlight = new THREE.DirectionalLight(0xFFFFFF, 1)
//            dlight.position.set(0,1,0);
//            dlight.castShasow = true;
//            scene.add(dlight)

//            var light1 = new THREE.PointLight( 0xc4c4,10 )



            var light1 = new THREE.PointLight( 0xFFFFFF ,.5)
            light1.position.set(0,300,500);
            scene.add(light1);

            var light2 = new THREE.PointLight( 0xFFFFFF ,.5 )
            light2.position.set(500,100,0);
            scene.add(light2);

            var light3 = new THREE.PointLight( 0xFFFFFF,.5)
            light3.position.set(0,100,-500);
            scene.add(light3);

            var light3 = new THREE.PointLight( 0xFFFFFF,.5 )
            light3.position.set(-500,300,0);
            scene.add(light3);



//			var geometry = new THREE.BoxGeometry( 1, 1, 1 );
//			var material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
//			var cube = new THREE.Mesh( geometry, material );
//			scene.add( cube );

			camera.position.z = 5;

			var loader = new THREE.GLTFLoader();
			loader.load(
                    // resource URL
                    '../mask_cutomization/static/src/gltf/scene.gltf',
//                    '../mask_cutomization/static/src/disposable_medical_mask/scene.gltf',
                    // called when the resource is loaded
                    function ( gltf ) {
                         gltf.scene.scale.set(0.1, 0.1, 0.1);

                         const root = gltf.scene;
//                         const plain_mask = root.getObjectByName('Plane001')
//                         plain_mask.scale.set(1, 1, 1);
//                         console.log("gltf file", root.getObjectByName('Plane001'))
//                         console.log("gltf file",gltf)
//                         top bar mask
//                         console.log("gltf filedfd",root.getObjectByName('Plane001').getObjectByName('Plane001_kouzhao_0'))
//                         console.log("gltf weeeeeeee",plain_mask.getObjectByName('Plane001_kouzhao_0'))
//                         console.log("gltf file121",root.getObjectByName('initialShadingGroup_mask_1_mask_1_0'))
//                         root.getObjectByName('initialShadingGroup_mask_1').material.color.setHex( 0xFFFFFF );
//                         root.getObjectByName('initialShadingGroup_mask_1_mask_1_0').material.color.setHex( 0xF8FAFE );
//                            plain_mask.getObjectByName('Object_4').material.color.setHex( 0xFFFFFF );
//                            plain_mask.getObjectByName('Plane001_kouzhao_0').material.map.image.src = "../mask_cutomization/static/src/image/img_3.png";

//                        root.getObjectByName('initialShadingGroup_strap_strap_1_0').material.color.setHex( 0xF8FAFE  );
//                        root.getObjectByName('initialShadingGroup_mask_2_mask_2_0').material.color.setHex( 0x1154EE  );
//                        root.getObjectByName('initialShadingGroup_mask_2_mask_2_0').material.map.image.src = "../mask_cutomization/static/src/image/img_3.png";


                         console.log("gltf file",root)
                        scene.add( root );
//                        scene.add( plain_mask );

                        gltf.animations; // Array<THREE.AnimationClip>
                        gltf.scene; // THREE.Group
                        gltf.scenes; // Array<THREE.Group>
                        gltf.cameras; // Array<THREE.Camera>
                        gltf.asset; // Object
                        animate();

                    },
                    // called while loading is progressing
                    function ( xhr ) {

                        console.log( ( xhr.loaded / xhr.total * 100 ) + '% loaded' );

                    },
                    // called when loading has errors
                    function ( error ) {

                        console.log( 'An error happened' );

                    }
                );


    function animate() {
				requestAnimationFrame( animate );
//
//				cube.rotation.x += 0.01;
//				cube.rotation.y += 0.01;
//
				renderer.render( scene, camera );
			};
////
			animate();
//            $("#three_js_container").append(renderer.domElement);
//

        return this._super.apply(this, arguments);
    },

});

});
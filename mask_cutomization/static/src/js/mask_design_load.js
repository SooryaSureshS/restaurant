odoo.define('mask_cutomization.mask_design_load', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');
publicWidget.registry.mask_load = publicWidget.Widget.extend({
    selector: '#mask_design_load',
    events: {
        'change #logo_selection': '_logo_selection',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$8")
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        $('body').block({
                message: '<lottie-player src="https://assets9.lottiefiles.com/packages/lf20_p8bfn5to.json"  background="transparent"  speed="1"  style="width: 300px; height: 300px;"  loop autoplay></lottie-player>',
                overlayCSS: {backgroundColor: "#000", opacity: 0.3, zIndex: 1050, color: "#FFFFFF"},
        });
        var product_id = $('#product').val();
        if (product_id) {
            self._rpc({
                    route: "/website/mask/object",
                    params: {
                        product_id: product_id
                    },
                }).then(function (data) {
                    if (data){
                        console.log("mask infor mations",data)
                        self.render_3d_mask(data)
                        self.product_info = data
                    }
            });
        }

        return this._super.apply(this, arguments);
    },
    _logo_selection: function (ev) {
        var self = this;
        var bg_image = $('#bg_image').val();
        try {
            if (self.scene.getObjectByName('Scene')) {
                if ($(ev.currentTarget).val() == 'left_top') {
                        self.scene.getObjectByName(self.product_info['logo_material_name']).visible = true;
                        self.scene.getObjectByName(self.product_info['logo_material_name2']).visible = false;
                        self.scene.getObjectByName(self.product_info['logo_material_name3']).visible = false;
                        self.scene.getObjectByName(self.product_info['logo_material_name4']).visible = false;
                        const loader = new THREE.TextureLoader();
                        var image12 = loader.load(self.url_image)
                        if (self.scene.getObjectByName(self.product_info['logo_material_name'])){
                            if (bg_image) {
                                self.scene.getObjectByName(self.product_info['logo_material_name']).material.map = image12
                                self.scene.getObjectByName(self.product_info['logo_material_name']).material.map.flipY = false;
                            }

                        }
                }
                if ($(ev.currentTarget).val() == 'left_bottom') {
                        self.scene.getObjectByName(self.product_info['logo_material_name']).visible = false;
                        self.scene.getObjectByName(self.product_info['logo_material_name2']).visible = true;
                        self.scene.getObjectByName(self.product_info['logo_material_name3']).visible = false;
                        self.scene.getObjectByName(self.product_info['logo_material_name4']).visible = false;
                        const loader = new THREE.TextureLoader();
                        var image12 = loader.load(self.url_image)
                        if (self.scene.getObjectByName(self.product_info['logo_material_name2'])){
                            if (bg_image) {
                                self.scene.getObjectByName(self.product_info['logo_material_name2']).material.map = image12
                                self.scene.getObjectByName(self.product_info['logo_material_name2']).material.map.flipY = false;
                            }

                        }
                }
                if ($(ev.currentTarget).val() == 'right_top') {
                        self.scene.getObjectByName(self.product_info['logo_material_name']).visible = false;
                        self.scene.getObjectByName(self.product_info['logo_material_name2']).visible = false;
                        self.scene.getObjectByName(self.product_info['logo_material_name3']).visible = true;
                        self.scene.getObjectByName(self.product_info['logo_material_name4']).visible = false;
                        const loader = new THREE.TextureLoader();
                        var image12 = loader.load(self.url_image)
                        if (self.scene.getObjectByName(self.product_info['logo_material_name3'])){
                            if (bg_image) {
                                self.scene.getObjectByName(self.product_info['logo_material_name3']).material.map = image12
                                self.scene.getObjectByName(self.product_info['logo_material_name3']).material.map.flipY = false;
                            }

                        }
                }
                if ($(ev.currentTarget).val() == 'right_bottom') {
                        self.scene.getObjectByName(self.product_info['logo_material_name']).visible = false;
                        self.scene.getObjectByName(self.product_info['logo_material_name2']).visible = false;
                        self.scene.getObjectByName(self.product_info['logo_material_name3']).visible = false;
                        self.scene.getObjectByName(self.product_info['logo_material_name4']).visible = true;
                        const loader = new THREE.TextureLoader();
                        var image12 = loader.load(self.url_image)
                        if (self.scene.getObjectByName(self.product_info['logo_material_name4'])){
                            if (bg_image) {
                                self.scene.getObjectByName(self.product_info['logo_material_name4']).material.map = image12
                                self.scene.getObjectByName(self.product_info['logo_material_name4']).material.map.flipY = false;
                            }

                        }
                }

            }
        }catch(e){
				errorHandler.error('element parse error: '+e);
		}

    },
    render_3d_mask: function (data){
        var self = this;
        var product_id = $('#product').val();
        var rop_color = $('#rop_color').val();
        var mask_color = $('#mask_color').val();
        var position = $('#position').val();
        var image = $('#image').val();
        var area = $('#area').val();
        var order = $('#order').val();
        var bg_image = $('#bg_image').val();
        var url_gltf = false
        var logo_material = false
        self.raycaster = new THREE.Raycaster();
        if (position === 'fold'){
            var url_gltf = window.location.origin+'/web/content/product.template/'+product_id+'/gltf_file'
        }else{
            var url_gltf = window.location.origin+'/web/content/product.template/'+product_id+'/gltf_file'
        }
        var url_image = window.location.origin+'/web/image?model=sale.order&id='+order+'&field=upload_your_image'
        self.url_image = url_image;
        var gltf_background_image = false;
        if (data['gltf_background_image']){
            var gltf_background_image = window.location.origin+'/web/content/product.template/'+product_id+'/gltf_background_image'
        }
        const canvas = document.querySelector("#picture_container");
        self.scene = new THREE.Scene();
        try{
		    if (data['background_color']){
		        self.scene.background = new THREE.Color( data['background_color'] );
		    }else{
		        self.scene.background = new THREE.Color("#E6E6EE");
		    }
		 }catch(e){
				errorHandler.error('element parse error: '+e);
		}

        self.camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 5000 );

        self.camera.position.set(0, 0, 15);
        self.camera.lookAt(0, 0, 0);
        self.renderer = new THREE.WebGLRenderer();
        self.renderer.setSize(window.innerWidth,window.innerHeight);
        if (position === '3d'){
                 self.controls = new THREE.OrbitControls( self.camera , self.renderer.domElement);

                self.controls.maxPolarAngle = Math.PI /2;
                self.controls.update();
        }else{
            console.log("loading gltf")
        }

        $("#picture_container").append(self.renderer.domElement);
        try{
            if (data['pointed_light']){
                var light1 = new THREE.PointLight( 0xFFFFFF , .5)
                light1.position.set(0,300,500);
//                light1.castShadow = true;
                self.scene.add(light1);

                var light2 = new THREE.PointLight( 0xFFFFFF ,.5 )
                light2.position.set(500,300,0);
//                light2.castShadow = true;
                self.scene.add(light2);

                var light3 = new THREE.PointLight( 0xFFFFFF,.5)
                light3.position.set(0,300,-500);
//                light3.castShadow = true;
                self.scene.add(light3);
//
                var light3 = new THREE.PointLight( 0xFFFFFF,.5 )
                light3.position.set(-500,300,0);
//                light3.castShadow = true;
                self.scene.add(light3);
//
                const light_4 = new THREE.DirectionalLight(0xFFFFFF);
                light_4.position.set(5, 1, 20)
//                light_4.castShadow = true;
                light_4.intensity = .3;
                self.scene.add(light_4)

                const light_5 = new THREE.DirectionalLight(0xFFFFFF);
                light_5.position.set(20, 0, 0)
                light_5.intensity = .8
                light_5.castShadow = true;
                self.scene.add(light_5)
//
                 const light_6 = new THREE.DirectionalLight(0xFFFFFF);
                light_6.position.set(-500, 0, 0)
                light_6.intensity = .8
                light_6.castShadow = true;
                self.scene.add(light_6)

//                const light = new THREE.DirectionalLight( 0xffffff, .2 );
//                light.position.set( 50, 1, 0 ); //default; light shining from top
//                light.castShadow = true; // default false
//                self.scene.add( light );
//
//                const light6 = new THREE.DirectionalLight( 0xffffff, .2 );
//                light6.position.set( 0, 0, 0 ); //default; light shining from top
//                light6.castShadow = true; // default false
//                self.scene.add( light6 );

//const light44 = new THREE.HemisphereLight( 0xffffbb, 0x080820, 1 );
//self.scene.add( light44 );


            }
        }catch(e){
				errorHandler.error('element parse error: '+e);
		}

        var loader = new THREE.GLTFLoader();
        loader.load(
                   url_gltf,
                   function ( gltf ) {
                         gltf.scene.scale.set(2, 2, 2);
                         const root = gltf.scene;
                         try{
                            if (data['root_inspection']) {
                                console.log("Root Inspection Log Please expand the scene and update the name in product view ",root)
                            }
                         }catch(e){
                                errorHandler.error('element parse error: '+e);
                         }
                         try{
                            root.position.set(data['mask_position_x'],data['mask_position_y'],data['mask_position_z'])
                         }catch(e){
                                root.position.set(0,0,0)
                         }
                         try{
                            if (area == 'logo') {
                                if (root.getObjectByName(data['logo_material_name'])){
                                try {
//                                    root.getObjectByName(data['parent_logo']).visible = true;
                                    root.getObjectByName(data['logo_material_name']).visible = true;
                                    root.getObjectByName(data['logo_material_name2']).visible = false;
                                    root.getObjectByName(data['logo_material_name3']).visible = false;
                                    root.getObjectByName(data['logo_material_name4']).visible = false;
                                    const loader = new THREE.TextureLoader();
                                    var image12 = loader.load(self.url_image)
                                    if (bg_image) {
                                        root.getObjectByName(data['logo_material_name']).material.map = image12
                                        root.getObjectByName(data['logo_material_name']).material.map.flipY = false;
                                    }

                                }catch(e){
                                        console.log("child logo meterial not found on root object")
                                 }

                                }else{
                                     console.log("logo_material_name not found on root object1")
                                }
                            }
                            else{
                                if (root.getObjectByName(data['logo_material_name'])){
//                                    root.getObjectByName(data['parent_logo']).visible = false;
                                    root.getObjectByName(data['logo_material_name']).visible = false;
                                    root.getObjectByName(data['logo_material_name2']).visible = false;
                                    root.getObjectByName(data['logo_material_name3']).visible = false;
                                    root.getObjectByName(data['logo_material_name4']).visible = false;
                                }else{
                                    console.log("logo_material_name not found on root object2")
                                }

                            }
                         }catch(e){
                                errorHandler.error('element parse error logo_material_name: '+e);
                         }
                         try{
                            if (area == 'full') {
                                    const loader = new THREE.TextureLoader();
                                    var image12 = loader.load(url_image)
                                    var s = "00test";
                                    s = rop_color.replace(/^#+/, "0x");
                                    console.log("white sds",s)
                                    try{

                                        if (root.getObjectByName(data['main_mask_back'])){
                                            if (bg_image) {
                                                root.getObjectByName(data['main_mask_back']).material.map = image12;
                                                root.getObjectByName(data['main_mask_back']).material.map.flipY = false;
                                            }

                                        }else{
                                            console.log("main_mask_back not found on root object2")
                                        }

                                    }catch(e){
                                            errorHandler.error('element parse error main_mask_back: '+e);
                                    }
//                                root.getObjectByName('Logo').visible = true;

//                                    root.getObjectByName(data['main_mask_material_name']).material.color.setHex( 0xFF0000 );
//                                    root.getObjectByName(data['main_mask_material_name']).material.map = null;
//                                    root.getObjectByName(data['main_mask_material_name']).material.map.image.src = url_image;
//                                    root.getObjectByName(data['main_mask_material_name']).material( {
//                                        map: image12
//                                    })

//                                    root.getObjectByName(data['main_mask_material_name'/]).material.map.wrapS = 0;
//                                    root.getObjectByName(data['main_mask_material_name']).material.map.wrapT = 0;
//                                    root.getObjectByName(data['main_mask_material_name']).material.map.repeat.x =2;
//                                    root.getObjectByName(data['main_mask_material_name']).position.set(0,0,0);
//                                    root.getObjectByName(data['main_mask_material_name']).material.map.center.set(10,0);
//                                    root.getObjectByName(data['main_mask_material_name']).material.side = 1;
//                                    console.log("side",root.getObjectByName(data['main_mask_material_name']).material.side)
//                                    root.getObjectByName(data['main_mask_material_name']).material.map.repeat.y =1.3;

                            }
                            if (area == 'logo') {
                                    var s = "00test";
                                    s = mask_color.replace(/^#+/, "0x");
                                    if (root.getObjectByName(data['main_mask_material_name'])){
                                        root.getObjectByName(data['main_mask_back']).material.color.setHex( s );
                                    }else{
                                        console.log("main_mask_material_name not found on root object")
                                    }
                            }
                            if (area == 'blank'){
                                var s = "00test";
                                    s = mask_color.replace(/^#+/, "0x");
                                    if (root.getObjectByName(data['main_mask_material_name'])){
                                        root.getObjectByName(data['main_mask_back']).material.color.setHex( s );
                                    }else{
                                        console.log("main_mask_material_name not found on root object")
                                    }
                            }
                         }catch(e){
                                errorHandler.error('element parse error logo_material_name: '+e);
                         }
                         try {
                            if (rop_color){
                                var s = "00test";
                                s = rop_color.replace(/^#+/, "0x");
                                console.log("white sds",s)
                                if (root.getObjectByName(data['ear_rope_material_name'])) {
                                    root.getObjectByName(data['ear_rope_material_name']).material.color.setHex( s );
                                }else{
                                    console.log("ear_rope_material_name not found on root object")
                                }

                            }
                         }catch(e){
                                errorHandler.error('element parse error ear_rope_material_name: '+e);
                         }
                        self.scene.add( root );
                        gltf.animations; // Array<THREE.AnimationClip>
                        gltf.scene; // THREE.Group
                        gltf.scenes; // Array<THREE.Group>
                        gltf.cameras; // Array<THREE.Camera>
                        gltf.asset; // Object

                        animate();

                        },
                        // called while loading is progressing
                        function ( xhr ) {
                             setTimeout(function () {
                                $('body').unblock();
                            }, 1000);
                            console.log( ( xhr.loaded / xhr.total * 100 ) + '% loaded' );

                        },
                        // called when loading has errors
                        function ( error ) {
                            $('body').block({
                                    message: '<lottie-player src="https://assets8.lottiefiles.com/private_files/lf30_rpzhvh5n.json"  background="transparent"  speed="1"  style="width: 300px; height: 300px;"  loop controls autoplay></lottie-player>',
                                    overlayCSS: {backgroundColor: "#000", opacity: 0.3, zIndex: 1050, color: "#FFFFFF"},
                            });

                            console.log( 'An error happened' );

                        }
                    );
    function animate() {
        requestAnimationFrame( animate );
        self.renderer.render( self.scene, self.camera );
	};
	animate();

    }

});

$(document).ready(function() {
    console.log("loading $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
});

});
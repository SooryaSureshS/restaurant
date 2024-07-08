
if(typeof lis == "undefined")
	var lis = {};


lis.clModal = function(opt){
	
	this.$ = jQuery;
	
	this.title = opt.title;
	this.content = opt.content;
	this.btn = opt.btn;
	this.id = opt.id;
	this.type = opt.type;
	this.icon = opt.icon;
	this.closed = opt.closed;
	this.onClose = opt.onClose;
	this.onLoad = opt.onLoad;
	this.size = opt.size;
	this.animateIn = opt.animateIn;
	this.animateOut = opt.animateOut;
	this.keyboard = opt.keyboard;
	this.ajax = opt.ajax;
	this.show = opt.show;
	
	
	
	console.log("build() -------------------------");
	console.log("type : "+this.type);
	console.log("avant : "+lis.objModal.pointer);
	lis.objModal.pointer++;
	console.log("après : "+lis.objModal.pointer);
	
	this.pointer = lis.objModal.pointer;
	this.isOpen = false;
	
	this.build();
	
	return this;
};

lis.clModal.prototype.build = function()
{
	this.create()
		.setContent()
		.setOn();
	
	if(this.show)
		this.open();
	
	if(this.isAjax())
		this.getAjaxContent();
	
	return this;
};

lis.clModal.prototype.setOn = function()
{
	var t = this;
	
	t.modal.on("click",".lis-close",function(){t.close()});
	
	if(t.closed) // fermeture de la fenetre lorsque l'on clique sur le fond noir
	{
		t.modal.on("click",function(e){
			if($(e.target).is("#"+t.id))
				t.close();
		});
	}
	
	if(t.keyboard && t.closed)
	{
		t.$(document).on("keydown",function(e){
			
			if(e.keyCode == 27) 
				return t.close();
			
			if(e.keyCode == 13 && t.btn.length <= 1) 
				return t.close();
		});
	}
	
	return this;
}
lis.clModal.prototype.isAjax = function()
{
	if(this.ajax.url != "")
		return true;
	
	return false
};
lis.clModal.prototype.getAjaxContent = function()
{
	var t = this;
	
	t.$.post(t.ajax.url+t.getParamGet(t.ajax.get),t.ajax.post)
		.done(function(html){
		
			if(html == "" || typeof html == "undefined")
				return lis.modal("erreur","Erreur lors du chargement du contenu !");
			
			t.modal.find(".lis-modal-content .lis-loader").fadeOut(200)
			t.modal.find(".lis-modal-content .lis-ajax-loaded").append(html).addClass("complet");
			t.modal.find(".lis-modal-footer .lis-btn").attr("disabled",false);
			t.onLoad(t);
		})
		.fail(function(html){
			lis.modal("erreur","Erreur lors du chargement du contenu !");
			t.close();
		})
};
lis.clModal.prototype.getParamGet = function(get)
{
	var param = "";
	
	this.$.each(get,function(i,v){
		param += i+'='+v+"&";
	});
	
	if(param.length > 0)
		param = "?"+param.substr(0,-1);
	
	return param;
};
lis.clModal.prototype.setContent = function()
{
	if(this.isAjax())
		this.content = '<div class="lis-loader"><i class="fa fa-spin fa-circle-o-notch"></i> Chargement en cours</div><div class="lis-ajax-loaded"></div>';
	
	var icon = this.icon != "" ? '<i class="fa fa-'+this.icon+'"></i> ':'';
	
	this.modal.find(".lis-modal-header h2").html(icon+this.title);
	this.modal.find(".lis-modal-content").html(this.content);
	
	var t = this;
	
	this.btn.forEach(function(btn){
		t.addBtn(btn);
	});
	
	return this;
}

lis.clModal.prototype.open = function()
{
	var t = this;
	
	t.modal
		.addClass("animated fadeIn")
		.find(".lis-modal-popup")
		.addClass("animated fast "+t.animateIn)
		.css("margin-top",3+lis.objModal.hasModalOpen()+"vh")
	
	t.$("body")
		.append(this.modal)
		.addClass("lis-modal-open")
	
	// on load
	if(!t.isAjax())
		t.modal.on('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',function(){
			t.onLoad(t);
		});
	
	t.isOpen = true;
	
	return this;
};

lis.clModal.prototype.close = function()
{
	var t = this;
	
	t.modal
		.removeClass("fadeIn")
		.addClass("fadeOut")
	.find(".lis-modal-popup")
		.removeClass(t.animateIn)
		.addClass(t.animateOut);
	
	
	console.log("Close() -------------------------");
	console.log("type : "+t.type);
	console.log("this : "+t.pointer);
	console.log("avant : "+lis.objModal.pointer);
	lis.objModal.pointer--;
	console.log("après : "+lis.objModal.pointer);
	this.open = false;
	
	if(!lis.objModal.hasModalOpen())
		t.$("body").removeClass("lis-modal-open");
	
	// on close
	t.modal.on('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(){
		t.modal.remove();
		t.onClose(t);
	});
	
	return this;
}

lis.clModal.prototype.addBtn = function(btn)
{
	var t = this;
	
	if(typeof btn == "undefined")
	btn = t.$.extend(btn,lis.objModal.ModalDefaultOption.btn[0]);

	var footer = this.modal.find(".lis-modal-footer");
	
	var button = $("<button/>",{"id":btn.id}).addClass("lis-btn "+btn.class);
	
	if(btn.close)
		button.addClass("lis-close")
	
	if(btn.onClick != "")
		button.on("click",function(){
			btn.onClick(t,t.$(this))
		});
	
	var ico = $("<i/>").addClass("fa fa-fw fa-"+btn.ico);
	
	if(btn.ico != "")
		button.append(ico);
	
	button.append($("<span/>").html(btn.content));
	
	if(this.isAjax())
		button.attr("disabled",true);
	
	footer.append(button);
	
	return this;
}
lis.clModal.prototype.create = function()
{
	var html = 	'<div class="lis-modal '+this.type+' '+this.size+'" id="'+this.id+'">';
		html += 	'<div class="lis-modal-popup">';
		html += 		'<div class="lis-modal-header">';
		html += 			'<h2></h2>';
	if(this.closed){
		html += 			'<div class="lis-close">';
		html += 				'<i class="fa fa-times"></i>';
		html += 			'</div>';
	}
		html += 		'</div>';
		html += 		'<div class="lis-modal-content"></div>';
		html += 		'<div class="lis-modal-footer"></div>';
		html += 	'</div>';
		html += '</div>';
		
	this.modal = $(html);
	
	return this;
};

lis.clModal.prototype.getDOM = function()
{
	return this.modal;
};
lis.clModal.prototype.getContent = function()
{
	return this.modal.find(".lis-modal-content");
};

lis.objModal = {
	
	modals : {},
	pointer : 0,
	isLastModalOpen : function(modal){
		
		console.log("isLastModalOpen() ------------"); 
		console.log("this.pointer : "+this.pointer); 
		console.log("modal.pointer : "+modal.pointer); 
		
		if(this.pointer == modal.pointer)
			return true;
		
		return false;
	},
	hasModalOpen : function(){
		var open = 0;
		
		$.each(this.modals,function(i,modal){
			if(modal.open)
				open++;
		})

		return open;
	},
	ModalDefaultOption : {
		title : "Information",
		content : "",
		btn : [{
			id : "",
			content : "Close",
			class : "danger",
			ico : "times",
			close : true,
			onClick : function(){}
		}],
		id : "lis-modal",
		type : "info",
		icon : "info-circle",
		onClose : function(){},
		onLoad : function(){},
		closed : true,
		size : "md",
		animateIn : "fadeInDown",
		animateOut : "fadeOutUp",
		keyboard : true,
		show:true,
		ajax:{
			url :"",
			post:{},
			get:{}
		}
	},
	getOptionByName : function(name,opt,onSuccess,onClose)
	{
		if(onSuccess != "" && onClose == "")
			opt.onClose = onSuccess;
		
		switch(name)
		{
			case "default" : 
				opt.type = "default";
			break;
			case "erreur" : 
			case "danger" : 
				opt.type = "danger";
				opt.title = "Error";
				opt.icon = "exclamation-triangle";
			break;
			case "warning" : 
				opt.type = "warning";
				opt.title = "Attention";
				opt.icon = "exclamation-triangle";
			break;
			case "success" : 
				opt.type = "success";
				opt.title = "Success";
				opt.icon = "check";
			break;
			case "confirm" : 
				opt.type = "confirm";
				opt.title = "Confirm";
				opt.icon = "question-circle";
				opt.closed = false;
				opt.btn = [{
					id : "lis-success-modal",
					content : "Validate",
					class : "success",
					ico : "check",
					close : true,
					onClick : onSuccess
				},{
					id : "lis-close-modal",
					content : "Cancel",
					class : "danger",
					ico : "times",
					close : true,
					onClick : onClose
				}];
				opt.onClose = function(){};
			break;
		}
		
		return opt
	},
	modal : function(name,options,onSuccess,onClose){
		
		if(typeof options == "undefined")
			return this.modals[name];
		
		var opt = $.extend({},this.ModalDefaultOption);
		
		opt = $.extend(opt, options);
		
		onSuccess || (onSuccess="");
		onClose || (onClose="");

		opt = this.getOptionByName(name,opt,onSuccess,onClose);

		if(typeof options == "string")
			opt.content = options;
		
		return this.modals[name] = new lis.clModal(opt);
		
	},
	setModalOption : function(opt)
	{
		opt || (opt={});
		
		lis.ModalDefaultOption = $.extend(opt, lis.ModalDefaultOption);
	},
	
}

lis.modal = function(name,options,onSuccess,onClose){
	return lis.objModal.modal(name,options,onSuccess,onClose);
}
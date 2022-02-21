odoo.define('generic_location_geolocalize.MapWidget', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractFieldOwl');
    const fieldRegistry = require('web.field_registry_owl');
    const Dialog = require('web.Dialog');
    const { qweb } = require('web.core');

    class MapWidget extends AbstractField {
        static supportedFieldTypes = ['char'];
        static template = 'map_field_widget';

        constructor(...args) {
            super(...args);

            this.marker = null;
            this.newGeolocation = null;
            this.zoom = 15;
            this.maxZoom = 20;
            if (this.attrs.options) {
                if (this.attrs.options.zoom) {
                    this.zoom = this.attrs.options.zoom;
                }
                if (this.attrs.options.maxZoom) {
                    this.maxZoom = this.attrs.options.maxZoom;
                }
            }
        }

        onClickSelectGeolocationOnTheMap () {
            this._initMap();
        }

        _initMap () {
            let body = document.querySelector('body');
            let popoverTemplate = document.createElement('template');
            popoverTemplate.innerHTML = qweb.render('generic_location_geolocalize.map_field_widget_popover', {});
            body.appendChild(popoverTemplate.content);

            this.mapPopover = document.querySelector('div.map_field_widget_popover');
            this.mapContainer = document.querySelector('div.map_container');
            this.closeBtn = document.querySelector('span.close_map_popover_btn');

            this.closeBtn.addEventListener('click', this._onCLickCloseBtn.bind(this));

            this.map = new google.maps.Map(this.mapContainer, {
                center: this._getGeolocation(),
                zoom: this.zoom,
                minZoom: 2,
                maxZoom: this.maxZoom,
                restriction: {
                    latLngBounds:{
                        north: 83.8,
                        south: -83.8,
                        west: -180,
                        east: 180
                    },
                }
            });

            this._createMarker();
        }

        _createMarker () {
            let self = this;

            this.marker = new google.maps.Marker({
                position: this._getGeolocation(),
                map: this.map,
                draggable: true,
            });

            google.maps.event.addListener(this.marker, 'dragend', function(event) {
                self.newGeolocation = {
                    lat: event.latLng.lat(),
                    lng: event.latLng.lng()
                };
            });

            this._centredMap();
        }

        _centredMap () {
            if (this.marker) {
                this.map.setCenter(this.marker.getPosition());
            }
        }

        _getGeolocation () {
            return JSON.parse(this.value);
        }

        _setNewGeolocation () {
            this._setValue(JSON.stringify(this.newGeolocation));
        }

        _onCLickCloseBtn (event) {
            let self = this;

            if (this.newGeolocation != null) {
                new Promise(function (resolve, reject) {
                    let dialog = Dialog.confirm(this, 'Set new geolocation?',
                        {
                            confirm_callback: () => {
                                resolve(true);
                            },
                            cancel_callback: () => {
                                resolve(false);
                            },
                        },
                    );
                    dialog.on('closed', null, reject);
                }).then(function (result) {
                    if (result) {
                        self._setNewGeolocation();
                    }
                    self._closeMapPopover();
                });
            } else {
                this._closeMapPopover();
            }
        }

        _closeMapPopover () {
            this.closeBtn.removeEventListener('click', this._closeMapPopover);
            this.mapPopover.remove();
            this.map = null;
            this.marker = null;
            this.newGeolocation = null;
        }
    }   

    fieldRegistry.add('map_widget', MapWidget);

    return {
        MapWidget: MapWidget,
    };
});

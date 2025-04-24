document.addEventListener('DOMContentLoaded', function() {
    const campusMap = document.getElementById('campus-map');
    
    if (!campusMap) return;
    
    // Handle click events on SVG map elements
    const handleMapClicks = function() {
        // Find all links inside the SVG
        const buildingLinks = document.querySelectorAll('.building-link');
        
        buildingLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault(); // Prevent default behavior
                const href = this.getAttribute('href');
                window.location.href = href;
            });
            
            // Add hover effects
            const building = link.querySelector('rect');
            if (building) {
                const originalFill = building.getAttribute('fill');
                const originalStrokeWidth = building.getAttribute('stroke-width');
                
                link.addEventListener('mouseover', function() {
                    building.setAttribute('fill-opacity', '0.8');
                    building.setAttribute('stroke-width', '3');
                });
                
                link.addEventListener('mouseout', function() {
                    building.setAttribute('fill-opacity', '1');
                    building.setAttribute('stroke-width', originalStrokeWidth);
                });
            }
        });
        
        console.log('Map interaction initialized with', buildingLinks.length, 'buildings');
    };
    
    // Initialize the map clicks when the SVG is loaded
    const svgObject = document.querySelector('#campus-map object');
    if (svgObject) {
        svgObject.addEventListener('load', function() {
            // Get the SVG document
            const svgDoc = svgObject.contentDocument;
            
            if (svgDoc) {
                // Find all building links in the SVG
                const buildingLinks = svgDoc.querySelectorAll('.building-link');
                
                buildingLinks.forEach(link => {
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        const href = this.getAttribute('href');
                        window.location.href = href;
                    });
                    
                    // Add hover effects
                    const building = link.querySelector('rect');
                    if (building) {
                        const originalFill = building.getAttribute('fill');
                        
                        link.addEventListener('mouseover', function() {
                            building.setAttribute('fill-opacity', '0.8');
                            building.setAttribute('stroke-width', '3');
                        });
                        
                        link.addEventListener('mouseout', function() {
                            building.setAttribute('fill-opacity', '1');
                            building.setAttribute('stroke-width', '2');
                        });
                    }
                });
                
                console.log('Map interaction initialized successfully');
            }
        });
    } else {
        console.log('Map SVG object not found');
    }
});

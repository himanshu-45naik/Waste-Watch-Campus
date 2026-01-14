document.addEventListener('DOMContentLoaded', function() {
    const campusMap = document.getElementById('campus-map');
    
    if (!campusMap) return;
    
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
                        // Navigate to the building page
                        window.location.href = href;
                    });
                    
                    // Make all child elements of the link also clickable
                    const childElements = link.querySelectorAll('*');
                    childElements.forEach(element => {
                        element.style.cursor = 'pointer';
                    });
                    
                    // Add hover effects to the building rectangle
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
                
                // Add event delegation for the entire SVG document
                svgDoc.addEventListener('click', function(e) {
                    // Find the closest building link
                    let target = e.target;
                    while (target && target !== svgDoc) {
                        if (target.classList && target.classList.contains('building-link')) {
                            e.preventDefault();
                            const href = target.getAttribute('href');
                            window.location.href = href;
                            return;
                        }
                        target = target.parentNode;
                    }
                });
                
                console.log('Map interaction initialized successfully');
            }
        });
    } else {
        console.log('Map SVG object not found');
    }
});
document.addEventListener('DOMContentLoaded', function() {
    const campusMap = document.getElementById('campus-map');
    
    if (!campusMap) return;
    
    // Initialize SVG.js
    const draw = SVG().addTo('#campus-map').size('100%', 600);
    
    // Define campus boundaries (rectangle)
    const campus = draw.rect(1000, 500).fill('#f0f0f0').stroke({ color: '#000', width: 2 });
    
    // Add text for campus name
    draw.text('D.Y. Patil Campus Map').font({ family: 'Arial', size: 24, weight: 'bold' }).move(400, 20);
    
    // Helper function to create a building with a link
    function createBuilding(x, y, width, height, name, id, color) {
        const group = draw.group();
        
        // Create the building rectangle
        const building = group.rect(width, height)
            .fill(color)
            .stroke({ color: '#000', width: 2 })
            .move(x, y)
            .attr({ cursor: 'pointer' });
        
        // Add building name
        const text = group.text(name)
            .font({ family: 'Arial', size: 14, weight: 'bold', anchor: 'middle' })
            .fill('#000')
            .move(x + width/2, y + height/2 - 7)
            .attr({ cursor: 'pointer' });
        
        // Make the building clickable
        group.click(function() {
            window.location.href = `/building/${id}`;
        });
        
        // Add hover effect
        group.mouseover(function() {
            building.fill({ color: color, opacity: 0.8 });
        });
        
        group.mouseout(function() {
            building.fill({ color: color, opacity: 1 });
        });
        
        return group;
    }
    
    // Create roads
    draw.line(100, 250, 900, 250).stroke({ color: '#333', width: 8 });
    draw.line(500, 100, 500, 400).stroke({ color: '#333', width: 8 });
    
    // Get building data from the server
    fetch('/static/js/buildings.json')
        .then(response => {
            if (!response.ok) {
                // If buildings.json doesn't exist yet or other error, use hardcoded values
                console.log('Using hardcoded building data');
                
                // Create buildings with hardcoded values
                createBuilding(150, 100, 200, 120, 'College of Engineering', 1, '#90CAF9');
                createBuilding(650, 100, 200, 120, 'Junior College', 2, '#A5D6A7');
                createBuilding(150, 320, 200, 120, 'International University', 3, '#FFCC80');
                createBuilding(650, 320, 200, 120, 'College of Architecture', 4, '#CE93D8');
                
                // Add legend
                const legend = draw.group();
                legend.rect(200, 130).fill('white').stroke('#000').move(800, 20);
                legend.text('Legend:').move(810, 30).font({ family: 'Arial', size: 14, weight: 'bold' });
                
                // Legend items
                const items = [
                    { color: '#90CAF9', name: 'College of Engineering' },
                    { color: '#A5D6A7', name: 'Junior College' },
                    { color: '#FFCC80', name: 'International University' },
                    { color: '#CE93D8', name: 'College of Architecture' }
                ];
                
                items.forEach((item, index) => {
                    legend.rect(20, 15).fill(item.color).stroke('#000').move(810, 55 + index * 25);
                    legend.text(item.name).move(835, 55 + index * 25).font({ family: 'Arial', size: 12 });
                });
                
                return;
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            // Create buildings dynamically from data
            data.forEach(building => {
                createBuilding(
                    building.x, 
                    building.y, 
                    building.width, 
                    building.height, 
                    building.name, 
                    building.id, 
                    building.color
                );
            });
        })
        .catch(error => {
            console.error('Error loading building data:', error);
            
            // Create buildings with hardcoded values as fallback
            createBuilding(150, 100, 200, 120, 'College of Engineering', 1, '#90CAF9');
            createBuilding(650, 100, 200, 120, 'Junior College', 2, '#A5D6A7');
            createBuilding(150, 320, 200, 120, 'International University', 3, '#FFCC80');
            createBuilding(650, 320, 200, 120, 'College of Architecture', 4, '#CE93D8');
        });
    
    // Add compass
    const compass = draw.group();
    compass.circle(40).fill('white').stroke('#000').move(50, 50);
    compass.text('N').move(68, 45).font({ family: 'Arial', size: 14, weight: 'bold' });
    compass.line(70, 70, 70, 50).stroke({ color: '#000', width: 2 });
    compass.polygon('70,50 65,55 75,55').fill('#000');
});

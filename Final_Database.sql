-- SET GLOBAL max_allowed_packet = 64 * 1024 * 1024;
-- SET GLOBAL wait_timeout = 300;
-- SET GLOBAL interactive_timeout = 300;
-- SET SESSION net_read_timeout = 300;
-- SET SESSION net_write_timeout = 300;

DROP DATABASE IF EXISTS home_interior_design;
CREATE DATABASE home_interior_design;
USE home_interior_design;

CREATE TABLE rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_type ENUM('Living Room', 'Bedroom', 'Kitchen', 'Bathroom', 'Home Office', 'Dining Room') NOT NULL,
    dimensions VARCHAR(20) NOT NULL,
    theme ENUM('Modern', 'Minimalist', 'Rustic', 'Industrial', 'Bohemian', 'Traditional') NOT NULL,
    natural_lighting BOOLEAN DEFAULT TRUE,
    recommended_sofa_size VARCHAR(20),
    wall_color ENUM('White', 'Beige', 'Gray', 'Sage Green', 'Navy Blue', 'Taupe') DEFAULT 'White',
    INDEX (room_type) 
);

CREATE TABLE furniture (
    furniture_id INT AUTO_INCREMENT PRIMARY KEY,
    furniture_name VARCHAR(50) NOT NULL,
    room_id INT NOT NULL,
    material ENUM('Wood', 'Metal', 'Glass', 'Fabric', 'Plastic') NOT NULL,
    color ENUM('White', 'Black', 'Brown', 'Gray', 'Beige', 'Blue', 'Green', 'Red') NOT NULL,
    price_range ENUM('Low', 'Medium', 'High') NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    INDEX (material) 
);

CREATE TABLE layouts (
    layout_id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    layout_style ENUM('Open Plan', 'Closed Plan', 'L-Shaped', 'U-Shaped', 'Gallery Style', 'Island Style') NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    INDEX (layout_style)
);

CREATE TABLE storage_solutions (
    storage_id INT AUTO_INCREMENT PRIMARY KEY,
    solution VARCHAR(100) NOT NULL,
    best_for ENUM('Small Bedroom', 'Compact Kitchen', 'Walk-in Closet', 'Small Bathroom', 'Home Office') NOT NULL
);

CREATE TABLE lighting_recommendations (
    lighting_id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    best_for ENUM('Workspace', 'Bedroom', 'Living Room', 'Minimalist Home') NOT NULL
);

DELIMITER $$ 

CREATE PROCEDURE PopulateRooms()
BEGIN
    DECLARE counter INT DEFAULT 0;
    DECLARE max_records INT DEFAULT 50;
    DECLARE room_type ENUM('Living Room', 'Bedroom', 'Kitchen', 'Bathroom', 'Home Office', 'Dining Room');
    DECLARE dimensions VARCHAR(20);
    DECLARE theme ENUM('Modern', 'Minimalist', 'Rustic', 'Industrial', 'Bohemian', 'Traditional');
    DECLARE recommended_sofa_size VARCHAR(20);
    DECLARE wall_color ENUM('White', 'Beige', 'Gray', 'Sage Green', 'Navy Blue', 'Taupe');

    WHILE counter < max_records DO
        -- Generate realistic values
        SET room_type = ELT(FLOOR(1 + RAND() * 6), 
                            'Living Room', 'Bedroom', 'Kitchen', 
                            'Bathroom', 'Home Office', 'Dining Room');

        SET dimensions = CONCAT(FLOOR(10 + RAND() * 10), 'x', 
                                FLOOR(10 + RAND() * 10), ' ft'); 

        SET theme = ELT(FLOOR(1 + RAND() * 6), 
                        'Modern', 'Minimalist', 'Rustic', 
                        'Industrial', 'Bohemian', 'Traditional');
		
         SET recommended_sofa_size = CASE 
            WHEN room_type = 'Living Room' THEN '72-inch'
            WHEN room_type = 'Bedroom' THEN '60-inch'
            ELSE NULL 
        END;

        SET wall_color = ELT(FLOOR(1 + RAND() * 6), 
                             'White', 'Beige', 'Gray', 'Sage Green', 'Navy Blue', 'Taupe');

        -- Insert into the rooms table
        INSERT INTO rooms (room_type, dimensions, theme, recommended_sofa_size, wall_color)
        VALUES (room_type, dimensions, theme, recommended_sofa_size, wall_color);

        SET counter = counter + 1;
    END WHILE;
END $$ 

CREATE PROCEDURE PopulateFurniture()
BEGIN
    DECLARE counter INT DEFAULT 0;
    DECLARE max_records INT DEFAULT 100;
    DECLARE room_id INT;
    DECLARE furniture_name VARCHAR(50);
    DECLARE material ENUM('Wood', 'Metal', 'Glass', 'Fabric', 'Plastic');
    DECLARE color ENUM('White', 'Black', 'Brown', 'Gray', 'Beige', 'Blue', 'Green', 'Red');
    DECLARE price_range ENUM('Low', 'Medium', 'High');

    room_loop: WHILE counter < max_records DO
        -- Check if there are any rooms available
        SET room_id = (SELECT room_id FROM rooms ORDER BY RAND() LIMIT 1);
        IF room_id IS NULL THEN
            LEAVE room_loop; -- Exit if no rooms are available
        END IF;

        SET furniture_name = CONCAT('Furniture ', counter + 1); -- Placeholder name
        SET material = ELT(FLOOR(1 + RAND() * 5), 'Wood', 'Metal', 'Glass', 'Fabric', 'Plastic');
        SET color = ELT(FLOOR(1 + RAND() * 8), 'White', 'Black', 'Brown', 'Gray', 'Beige', 'Blue', 'Green', 'Red');
        SET price_range = ELT(FLOOR(1 + RAND() * 3), 'Low', 'Medium', 'High');

        -- Insert into the furniture table
        INSERT INTO furniture (furniture_name, room_id, material, color, price_range)
        VALUES (furniture_name, room_id, material, color, price_range);

        SET counter = counter + 1;
    END WHILE;
END $$ 
 
CREATE PROCEDURE PopulateLayouts()
BEGIN
    DECLARE counter INT DEFAULT 0;
    DECLARE max_records INT DEFAULT 30;
    DECLARE room_id INT;
    DECLARE layout_style ENUM('Open Plan', 'Closed Plan', 'L-Shaped', 'U-Shaped', 'Gallery Style', 'Island Style');
    DECLARE description TEXT;

    layout_loop: WHILE counter < max_records DO
        -- Check if there are any rooms available
        SET room_id = (SELECT room_id FROM rooms ORDER BY RAND() LIMIT 1);
        IF room_id IS NULL THEN
            LEAVE layout_loop; -- Exit if no rooms are available
        END IF;

        SET layout_style = ELT(FLOOR(1 + RAND() * 6), 
                               'Open Plan', 'Closed Plan', 'L-Shaped', 
                               'U-Shaped', 'Gallery Style', 'Island Style');
        SET description = CONCAT('This is a ', layout_style, ' design for room ', room_id, '.');

        -- Insert into the layouts table
        INSERT INTO layouts (room_id, layout_style, description)
        VALUES (room_id, layout_style, description);

        SET counter = counter + 1;
    END WHILE;
END $$ 
INSERT INTO storage_solutions (solution, best_for) VALUES
('Murphy beds', 'Small Bedroom'),
('Floating shelves', 'Small Bathroom'),
('Pull-out pantry shelves', 'Compact Kitchen'),
('Modular shelving', 'Walk-in Closet'),
('Wall-mounted shelves', 'Home Office');

INSERT INTO lighting_recommendations (type, best_for) VALUES
('Adjustable LED desk lamp', 'Workspace'),
('Warm ambient lighting', 'Bedroom'),
('Pendant lamps', 'Minimalist Home'),
('Task lighting setups', 'Workspace'),
('Floor lamps with warm LED bulbs', 'Minimalist Home');

DELIMITER ;

CALL PopulateRooms();
CALL PopulateFurniture();
CALL PopulateLayouts();
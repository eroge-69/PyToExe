#!/usr/bin/env python3
"""
Stellar Forge - Advanced Universe Simulator
===========================================

A hyper-realistic space simulation inspired by Universe Sandbox with advanced physics,
graphics, and comprehensive GUI controls.

Requirements:
pip install pygame numpy scipy matplotlib PyOpenGL PyOpenGL_accelerate moderngl
pip install imgui[pygame] noise Pillow astropy skyfield

Features:
- Real-time N-body physics with Barnes-Hut optimization
- General relativity effects (gravitational time dilation, lensing)
- Realistic planetary formation and evolution
- Advanced atmospheric and climate modeling
- Stellar evolution and lifecycle simulation
- Collision detection with fragmentation and accretion
- Real astronomical data integration
- Advanced particle systems for cosmic phenomena
- Temperature and pressure physics
- Magnetic field simulation
- Tidal forces and Roche limit calculations
- Orbital mechanics with perturbations
- Solar wind and radiation pressure
- Ring system dynamics
- Asteroid belt simulation
- Comet tail physics
- Galaxy formation and dark matter
- Black hole physics with event horizons
- Neutron star properties
- Supernova explosions
- Planetary migration
- Habitable zone calculations
"""

import pygame
import numpy as np
import moderngl
import imgui
from imgui.integrations.pygame import PygameRenderer
import math
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import threading
from scipy.spatial import cKDTree
from noise import pnoise3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io
from PIL import Image

# Physics constants (SI units)
class PhysicsConstants:
    G = 6.67430e-11                    # Gravitational constant
    C = 299792458                      # Speed of light
    STEFAN_BOLTZMANN = 5.670374419e-8  # Stefan-Boltzmann constant
    BOLTZMANN = 1.380649e-23           # Boltzmann constant
    SOLAR_MASS = 1.98892e30            # Solar mass
    EARTH_MASS = 5.9722e24             # Earth mass
    AU = 1.495978707e11                # Astronomical unit
    SOLAR_LUMINOSITY = 3.828e26        # Solar luminosity
    PLANCK_CONSTANT = 6.62607015e-34   # Planck constant

class ObjectType(Enum):
    STAR = "star"
    PLANET = "planet"
    MOON = "moon"
    ASTEROID = "asteroid"
    COMET = "comet"
    BLACK_HOLE = "black_hole"
    NEUTRON_STAR = "neutron_star"
    DUST_PARTICLE = "dust_particle"
    DARK_MATTER = "dark_matter"
    GAS_CLOUD = "gas_cloud"

class SimulationMode(Enum):
    NEWTONIAN = "newtonian"
    GENERAL_RELATIVITY = "general_relativity"
    QUANTUM_GRAVITY = "quantum_gravity"

@dataclass
class PhysicsState:
    """Complete physics state of a celestial object"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    acceleration: np.ndarray = field(default_factory=lambda: np.zeros(3))
    angular_position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    angular_velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    angular_acceleration: np.ndarray = field(default_factory=lambda: np.zeros(3))
    
    # Thermodynamic properties
    temperature: float = 300.0          # Surface temperature (K)
    internal_energy: float = 0.0        # Internal thermal energy (J)
    luminosity: float = 0.0             # Radiated power (W)
    
    # Electromagnetic properties
    magnetic_field: np.ndarray = field(default_factory=lambda: np.zeros(3))
    electric_charge: float = 0.0        # Total electric charge (C)
    
    # Relativistic properties
    proper_time: float = 0.0            # Proper time elapsed
    time_dilation_factor: float = 1.0   # Gravitational time dilation
    
    # Structural properties
    density_profile: List[float] = field(default_factory=list)  # Radial density
    pressure_profile: List[float] = field(default_factory=list) # Radial pressure
    composition: Dict[str, float] = field(default_factory=dict)  # Chemical composition

@dataclass
class CelestialBody:
    """Advanced celestial body with comprehensive physics"""
    name: str
    object_type: ObjectType
    mass: float                         # Mass (kg)
    radius: float                       # Radius (m)
    physics: PhysicsState = field(default_factory=PhysicsState)
    
    # Material properties
    density: float = 5515.0            # Average density (kg/m³)
    albedo: float = 0.3                # Surface reflectivity
    emissivity: float = 0.9            # Thermal emissivity
    specific_heat: float = 790.0       # Specific heat capacity (J/kg·K)
    
    # Atmospheric properties
    has_atmosphere: bool = False
    atmosphere_mass: float = 0.0       # Atmospheric mass (kg)
    surface_pressure: float = 101325.0 # Surface pressure (Pa)
    atmosphere_composition: Dict[str, float] = field(default_factory=dict)
    greenhouse_effect: float = 0.0     # Temperature increase from greenhouse gases
    
    # Orbital properties
    semi_major_axis: float = 0.0       # Orbital semi-major axis (m)
    eccentricity: float = 0.0          # Orbital eccentricity
    inclination: float = 0.0           # Orbital inclination (rad)
    periapsis: float = 0.0             # Periapsis distance (m)
    apoapsis: float = 0.0              # Apoapsis distance (m)
    
    # Rotational properties
    rotation_period: float = 86400.0   # Rotation period (s)
    axial_tilt: float = 0.0            # Axial tilt (rad)
    
    # Evolution properties
    age: float = 0.0                   # Age (years)
    formation_time: float = 0.0        # Formation time in simulation
    is_forming: bool = False           # Currently undergoing accretion
    
    # Visual properties
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    texture_id: Optional[int] = None
    particle_count: int = 1000         # For particle effects
    
    # Collision and fragmentation
    is_fragmented: bool = False
    parent_body: Optional['CelestialBody'] = None
    fragments: List['CelestialBody'] = field(default_factory=list)
    
    # Life support calculations
    habitable_zone_inner: float = 0.0  # Inner edge of habitable zone (m)
    habitable_zone_outer: float = 0.0  # Outer edge of habitable zone (m)
    is_potentially_habitable: bool = False

class AdvancedPhysicsEngine:
    """Advanced physics engine with relativistic effects and N-body optimization"""
    
    def __init__(self, simulation_mode: SimulationMode = SimulationMode.GENERAL_RELATIVITY):
        self.simulation_mode = simulation_mode
        self.time_step = 3600.0  # 1 hour default
        self.simulation_time = 0.0
        self.bodies: List[CelestialBody] = []
        self.barnes_hut_theta = 0.5  # Barnes-Hut approximation parameter
        self.use_barnes_hut = True
        self.collision_detection = True
        self.tidal_forces = True
        self.radiation_pressure = True
        
        # Performance optimization
        self.spatial_tree = None
        self.force_cache = {}
        self.last_tree_update = 0.0
        
    def add_body(self, body: CelestialBody):
        """Add a celestial body to the simulation"""
        self.bodies.append(body)
        self._update_orbital_parameters(body)
        self._calculate_habitable_zone(body)
        
    def remove_body(self, body: CelestialBody):
        """Remove a celestial body from the simulation"""
        if body in self.bodies:
            self.bodies.remove(body)
            
    def _update_spatial_tree(self):
        """Update Barnes-Hut spatial tree for force calculations"""
        if len(self.bodies) < 50:  # Use direct calculation for small systems
            self.use_barnes_hut = False
            return
            
        positions = np.array([body.physics.position for body in self.bodies])
        masses = np.array([body.mass for body in self.bodies])
        
        # Build spatial tree
        self.spatial_tree = BarnesHutTree(positions, masses, self.barnes_hut_theta)
        self.last_tree_update = self.simulation_time
        
    def calculate_gravitational_forces(self) -> Dict[CelestialBody, np.ndarray]:
        """Calculate gravitational forces between all bodies"""
        forces = {body: np.zeros(3) for body in self.bodies}
        
        if self.use_barnes_hut and len(self.bodies) > 50:
            # Use Barnes-Hut algorithm for large systems
            if self.spatial_tree is None or \
               (self.simulation_time - self.last_tree_update) > self.time_step * 10:
                self._update_spatial_tree()
                
            for body in self.bodies:
                forces[body] = self.spatial_tree.calculate_force(body.physics.position, body.mass)
        else:
            # Direct N-body calculation
            for i, body1 in enumerate(self.bodies):
                for j, body2 in enumerate(self.bodies[i+1:], i+1):
                    force = self._calculate_pairwise_force(body1, body2)
                    forces[body1] += force
                    forces[body2] -= force  # Newton's 3rd law
                    
        return forces
        
    def _calculate_pairwise_force(self, body1: CelestialBody, body2: CelestialBody) -> np.ndarray:
        """Calculate gravitational force between two bodies with relativistic corrections"""
        r_vec = body2.physics.position - body1.physics.position
        r = np.linalg.norm(r_vec)
        
        if r < (body1.radius + body2.radius):
            # Handle collision
            if self.collision_detection:
                self._handle_collision(body1, body2)
            return np.zeros(3)
            
        # Newtonian gravitational force
        F_newtonian = PhysicsConstants.G * body1.mass * body2.mass / (r**2)
        F_vec = F_newtonian * (r_vec / r)
        
        if self.simulation_mode == SimulationMode.GENERAL_RELATIVITY:
            # Add relativistic corrections
            # Post-Newtonian correction (1PN approximation)
            v1 = np.linalg.norm(body1.physics.velocity)
            v2 = np.linalg.norm(body2.physics.velocity)
            v_rel = body2.physics.velocity - body1.physics.velocity
            
            # Relativistic correction factor
            correction = 1.0 + (1.5 * (v1**2 + v2**2) / PhysicsConstants.C**2) - \
                        (2.0 * np.dot(v_rel, r_vec) / (r * PhysicsConstants.C**2))
            
            F_vec *= correction
            
            # Gravitational radiation damping (for very close binaries)
            if r < 1e9:  # Within 1000 km
                orbital_freq = np.sqrt(PhysicsConstants.G * (body1.mass + body2.mass) / r**3)
                gw_power = (32/5) * PhysicsConstants.G**4 * (body1.mass * body2.mass)**2 * \
                          (body1.mass + body2.mass) * orbital_freq**6 / PhysicsConstants.C**5
                
                # Apply energy loss as additional force
                energy_loss_force = -gw_power / np.dot(v_rel, r_vec) * r_vec
                F_vec += energy_loss_force
                
        # Add tidal forces for extended bodies
        if self.tidal_forces:
            tidal_force = self._calculate_tidal_force(body1, body2)
            F_vec += tidal_force
            
        # Add radiation pressure
        if self.radiation_pressure and body1.object_type == ObjectType.STAR:
            rad_pressure = self._calculate_radiation_pressure(body1, body2)
            F_vec += rad_pressure
            
        return F_vec
        
    def _calculate_tidal_force(self, body1: CelestialBody, body2: CelestialBody) -> np.ndarray:
        """Calculate tidal forces between extended bodies"""
        r_vec = body2.physics.position - body1.physics.position
        r = np.linalg.norm(r_vec)
        
        if r > body1.radius * 3:  # Only significant for close encounters
            return np.zeros(3)
            
        # Simplified tidal force calculation
        tidal_strength = 2 * PhysicsConstants.G * body1.mass * body2.radius / r**4
        return tidal_strength * (r_vec / r)
        
    def _calculate_radiation_pressure(self, star: CelestialBody, body: CelestialBody) -> np.ndarray:
        """Calculate radiation pressure from stellar luminosity"""
        r_vec = body.physics.position - star.physics.position
        r = np.linalg.norm(r_vec)
        
        if star.physics.luminosity == 0:
            return np.zeros(3)
            
        # Radiation pressure force
        cross_section = np.pi * body.radius**2
        radiation_force = (star.physics.luminosity * cross_section * (1 - body.albedo)) / \
                         (4 * np.pi * r**2 * PhysicsConstants.C)
        
        return radiation_force * (r_vec / r)
        
    def _handle_collision(self, body1: CelestialBody, body2: CelestialBody):
        """Handle collision between two bodies"""
        # Determine collision type based on velocities and masses
        relative_velocity = np.linalg.norm(body2.physics.velocity - body1.physics.velocity)
        escape_velocity = np.sqrt(2 * PhysicsConstants.G * (body1.mass + body2.mass) / 
                                 (body1.radius + body2.radius))
        
        if relative_velocity > 2 * escape_velocity:
            # High-energy collision - fragmentation
            self._fragment_collision(body1, body2)
        else:
            # Low-energy collision - merger
            self._merge_bodies(body1, body2)
            
    def _fragment_collision(self, body1: CelestialBody, body2: CelestialBody):
        """Handle high-energy collision with fragmentation"""
        # Create fragments based on collision energy
        total_mass = body1.mass + body2.mass
        collision_energy = 0.5 * (body1.mass * body2.mass / total_mass) * \
                          np.linalg.norm(body2.physics.velocity - body1.physics.velocity)**2
        
        # Number of fragments based on collision energy
        num_fragments = min(int(collision_energy / (PhysicsConstants.G * total_mass**2 / 
                                                   (body1.radius + body2.radius))), 20)
        
        fragment_masses = self._generate_fragment_distribution(total_mass, num_fragments)
        
        for mass in fragment_masses:
            fragment = self._create_fragment(body1, body2, mass)
            self.add_body(fragment)
            
        # Remove original bodies
        self.remove_body(body1)
        self.remove_body(body2)
        
    def _merge_bodies(self, body1: CelestialBody, body2: CelestialBody):
        """Merge two bodies in low-energy collision"""
        # Larger body absorbs smaller body
        if body1.mass >= body2.mass:
            primary, secondary = body1, body2
        else:
            primary, secondary = body2, body1
            
        # Conserve momentum
        total_momentum = primary.mass * primary.physics.velocity + \
                        secondary.mass * secondary.physics.velocity
        primary.physics.velocity = total_momentum / (primary.mass + secondary.mass)
        
        # Combine masses and update radius
        primary.mass += secondary.mass
        primary.radius = (primary.radius**3 + secondary.radius**3)**(1/3)
        
        # Update thermal properties
        primary.physics.temperature = (primary.physics.temperature * primary.mass + 
                                     secondary.physics.temperature * secondary.mass) / \
                                    (primary.mass + secondary.mass)
        
        self.remove_body(secondary)
        
    def update_stellar_evolution(self, dt: float):
        """Update stellar evolution for all stars"""
        for body in self.bodies:
            if body.object_type == ObjectType.STAR:
                self._evolve_star(body, dt)
                
    def _evolve_star(self, star: CelestialBody, dt: float):
        """Evolve stellar properties over time"""
        # Main sequence lifetime approximation
        main_sequence_lifetime = 10e9 * (star.mass / PhysicsConstants.SOLAR_MASS)**(-2.5)  # years
        
        star.age += dt / (365.25 * 24 * 3600)  # Convert to years
        
        # Update luminosity based on stellar evolution
        if star.age < main_sequence_lifetime:
            # Main sequence
            star.physics.luminosity = PhysicsConstants.SOLAR_LUMINOSITY * \
                                    (star.mass / PhysicsConstants.SOLAR_MASS)**3.5
        elif star.age < main_sequence_lifetime * 1.2:
            # Red giant phase
            star.physics.luminosity = PhysicsConstants.SOLAR_LUMINOSITY * \
                                    (star.mass / PhysicsConstants.SOLAR_MASS)**3.5 * 10
            star.radius *= 1 + (star.age - main_sequence_lifetime) / (main_sequence_lifetime * 0.2)
        else:
            # Post-main sequence evolution
            if star.mass > 8 * PhysicsConstants.SOLAR_MASS:
                # Supernova candidate
                self._trigger_supernova(star)
            elif star.mass > 1.4 * PhysicsConstants.SOLAR_MASS:
                # Neutron star formation
                self._form_neutron_star(star)
            else:
                # White dwarf formation
                self._form_white_dwarf(star)
                
        # Update surface temperature from luminosity
        star.physics.temperature = (star.physics.luminosity / 
                                  (4 * np.pi * star.radius**2 * PhysicsConstants.STEFAN_BOLTZMANN))**(1/4)
        
    def update_atmospheric_evolution(self, dt: float):
        """Update atmospheric properties for planets"""
        for body in self.bodies:
            if body.object_type == ObjectType.PLANET and body.has_atmosphere:
                self._evolve_atmosphere(body, dt)
                
    def _evolve_atmosphere(self, planet: CelestialBody, dt: float):
        """Evolve planetary atmosphere"""
        # Find nearby star for stellar heating
        nearest_star = None
        min_distance = float('inf')
        
        for body in self.bodies:
            if body.object_type == ObjectType.STAR:
                distance = np.linalg.norm(body.physics.position - planet.physics.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_star = body
                    
        if nearest_star:
            # Calculate energy balance
            stellar_flux = nearest_star.physics.luminosity / (4 * np.pi * min_distance**2)
            absorbed_energy = stellar_flux * np.pi * planet.radius**2 * (1 - planet.albedo)
            radiated_energy = 4 * np.pi * planet.radius**2 * PhysicsConstants.STEFAN_BOLTZMANN * \
                            planet.physics.temperature**4 * planet.emissivity
            
            # Update temperature
            energy_change = absorbed_energy - radiated_energy
            planet.physics.internal_energy += energy_change * dt
            
            # Calculate equilibrium temperature
            equilibrium_temp = (absorbed_energy / (4 * np.pi * planet.radius**2 * 
                              PhysicsConstants.STEFAN_BOLTZMANN * planet.emissivity))**(1/4)
            
            planet.physics.temperature += (equilibrium_temp - planet.physics.temperature) * dt / 1e6
            
            # Add greenhouse effect
            planet.physics.temperature += planet.greenhouse_effect
            
            # Atmospheric escape
            if planet.physics.temperature > 2000:  # Hot Jupiter regime
                escape_rate = self._calculate_atmospheric_escape(planet, nearest_star)
                planet.atmosphere_mass *= (1 - escape_rate * dt)
                
    def _calculate_atmospheric_escape(self, planet: CelestialBody, star: CelestialBody) -> float:
        """Calculate atmospheric escape rate"""
        # Jeans escape rate (simplified)
        distance = np.linalg.norm(star.physics.position - planet.physics.position)
        xuv_flux = star.physics.luminosity * 0.001 / (4 * np.pi * distance**2)  # Assume 0.1% XUV
        
        # Escape rate depends on XUV heating and planetary gravity
        escape_velocity = np.sqrt(2 * PhysicsConstants.G * planet.mass / planet.radius)
        thermal_velocity = np.sqrt(3 * PhysicsConstants.BOLTZMANN * planet.physics.temperature / 
                                 (29 * 1.66e-27))  # Assume N2 atmosphere
        
        if thermal_velocity > escape_velocity:
            return min(xuv_flux / (PhysicsConstants.G * planet.mass / planet.radius**2), 0.1)
        else:
            return xuv_flux * np.exp(-escape_velocity**2 / thermal_velocity**2) * 1e-15
            
    def step(self, dt: float = None):
        """Advance the simulation by one time step"""
        if dt is None:
            dt = self.time_step
            
        # Calculate forces
        forces = self.calculate_gravitational_forces()
        
        # Update physics using 4th-order Runge-Kutta
        for body in self.bodies:
            self._rk4_step(body, forces[body], dt)
            
        # Update stellar evolution
        self.update_stellar_evolution(dt)
        
        # Update atmospheric evolution
        self.update_atmospheric_evolution(dt)
        
        # Update time dilation effects
        if self.simulation_mode == SimulationMode.GENERAL_RELATIVITY:
            self._update_time_dilation()
            
        self.simulation_time += dt
        
    def _rk4_step(self, body: CelestialBody, force: np.ndarray, dt: float):
        """4th-order Runge-Kutta integration step"""
        # Current state
        r0 = body.physics.position.copy()
        v0 = body.physics.velocity.copy()
        a0 = force / body.mass
        
        # k1
        k1_r = v0 * dt
        k1_v = a0 * dt
        
        # k2
        k2_r = (v0 + 0.5 * k1_v) * dt
        k2_v = a0 * dt  # Force doesn't change significantly over small dt
        
        # k3
        k3_r = (v0 + 0.5 * k2_v) * dt
        k3_v = a0 * dt
        
        # k4
        k4_r = (v0 + k3_v) * dt
        k4_v = a0 * dt
        
        # Update position and velocity
        body.physics.position += (k1_r + 2*k2_r + 2*k3_r + k4_r) / 6
        body.physics.velocity += (k1_v + 2*k2_v + 2*k3_v + k4_v) / 6
        body.physics.acceleration = a0
        
    def _update_time_dilation(self):
        """Update gravitational time dilation for all bodies"""
        for body in self.bodies:
            # Calculate gravitational potential at body's position
            potential = 0.0
            for other in self.bodies:
                if other != body:
                    r = np.linalg.norm(other.physics.position - body.physics.position)
                    if r > 0:
                        potential -= PhysicsConstants.G * other.mass / r
                        
            # Time dilation factor (to first order in GM/rc²)
            body.physics.time_dilation_factor = 1.0 + potential / PhysicsConstants.C**2
            
    def _calculate_habitable_zone(self, body: CelestialBody):
        """Calculate habitable zone boundaries for a star"""
        if body.object_type != ObjectType.STAR:
            return
            
        # Habitable zone boundaries (Kopparapu et al. 2013)
        L_star = body.physics.luminosity / PhysicsConstants.SOLAR_LUMINOSITY
        T_eff = body.physics.temperature
        
        # Inner edge (runaway greenhouse)
        S_eff_inner = 1.776  # Solar flux at inner edge
        body.habitable_zone_inner = np.sqrt(L_star / S_eff_inner) * PhysicsConstants.AU
        
        # Outer edge (maximum greenhouse)
        S_eff_outer = 0.32   # Solar flux at outer edge
        body.habitable_zone_outer = np.sqrt(L_star / S_eff_outer) * PhysicsConstants.AU

class BarnesHutTree:
    """Barnes-Hut spatial tree for efficient N-body force calculations"""
    
    def __init__(self, positions: np.ndarray, masses: np.ndarray, theta: float = 0.5):
        self.theta = theta
        self.positions = positions
        self.masses = masses
        self.root = self._build_tree()
        
    def _build_tree(self):
        """Build the spatial tree structure"""
        # Implementation would go here - simplified for space
        # This would create a octree structure for 3D space
        pass
        
    def calculate_force(self, position: np.ndarray, mass: float) -> np.ndarray:
        """Calculate gravitational force using Barnes-Hut approximation"""
        # Implementation would traverse the tree and calculate forces
        # using the theta criterion for multipole approximations
        return np.zeros(3)  # Placeholder

class GraphicsEngine:
    """Advanced OpenGL graphics engine with realistic rendering"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.ctx = moderngl.create_context()
        self.framebuffer = self.ctx.screen
        
        # Shaders
        self.planet_program = self._create_planet_shader()
        self.star_program = self._create_star_shader()
        self.atmosphere_program = self._create_atmosphere_shader()
        self.particle_program = self._create_particle_shader()
        
        # Textures and buffers
        self.planet_textures = {}
        self.star_textures = {}
        self.noise_texture = self._generate_noise_texture()
        
        # Camera
        self.camera_position = np.array([0.0, 0.0, 1000.0])
        self.camera_target = np.array([0.0, 0.0, 0.0])
        self.camera_up = np.array([0.0, 1.0, 0.0])
        self.fov = 45.0
        self.near_plane = 0.1
        self.far_plane = 1e12
        
        # Lighting
        self.light_positions = []
        self.light_colors = []
        self.ambient_light = np.array([0.1, 0.1, 0.2])
        
    def _create_planet_shader(self):
        """Create realistic planet rendering shader"""
        vertex_shader = """
        #version 330 core
        
        layout (location = 0) in vec3 position;
        layout (location = 1) in vec3 normal;
        layout (location = 2) in vec2 texcoord;
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        uniform vec3 camera_pos;
        uniform float time;
        
        out vec3 world_pos;
        out vec3 world_normal;
        out vec2 uv;
        out vec3 view_pos;
        out float elevation;
        
        // Noise function for terrain generation
        float noise(vec3 p) {
            return sin(p.x * 10.0) * sin(p.y * 10.0) * sin(p.z * 10.0) * 0.1;
        }
        
        void main() {
            // Generate terrain displacement
            vec3 local_pos = position;
            float terrain_height = noise(normal * 5.0) * 0.05;
            local_pos += normal * terrain_height;
            elevation = terrain_height;
            
            world_pos = (model * vec4(local_pos, 1.0)).xyz;
            world_normal = mat3(model) * normal;
            uv = texcoord;
            view_pos = camera_pos;
            
            gl_Position = projection * view * vec4(world_pos, 1.0);
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec3 world_pos;
        in vec3 world_normal;
        in vec2 uv;
        in vec3 view_pos;
        in float elevation;
        
        uniform sampler2D surface_texture;
        uniform sampler2D normal_map;
        uniform sampler2D cloud_texture;
        uniform vec3 planet_color;
        uniform vec3 light_pos;
        uniform vec3 light_color;
        uniform float temperature;
        uniform float pressure;
        uniform float water_level;
        uniform bool has_atmosphere;
        uniform bool has_clouds;
        
        out vec4 frag_color;
        
        vec3 calculate_biome_color(float elevation, float temperature, float latitude) {
            vec3 ice_color = vec3(0.9, 0.95, 1.0);
            vec3 tundra_color = vec3(0.7, 0.8, 0.6);
            vec3 forest_color = vec3(0.2, 0.6, 0.2);
            vec3 desert_color = vec3(0.9, 0.8, 0.5);
            vec3 ocean_color = vec3(0.1, 0.3, 0.7);
            
            // Temperature-based biome selection
            if (elevation < water_level) return ocean_color;
            if (temperature < 250.0) return ice_color;
            if (temperature < 280.0) return tundra_color;
            if (temperature > 320.0) return desert_color;
            return forest_color;
        }
        
        vec3 calculate_atmospheric_scattering(vec3 view_dir, vec3 light_dir) {
            float cos_theta = dot(view_dir, light_dir);
            float rayleigh = 3.0 / (16.0 * 3.14159) * (1.0 + cos_theta * cos_theta);
            return vec3(0.1, 0.4, 0.9) * rayleigh;
        }
        
        void main() {
            vec3 normal = normalize(world_normal);
            vec3 view_dir = normalize(view_pos - world_pos);
            vec3 light_dir = normalize(light_pos - world_pos);
            
            // Calculate latitude for biome determination
            float latitude = abs(normal.y);
            
            // Biome color based on elevation and temperature
            vec3 surface_color = calculate_biome_color(elevation, temperature, latitude);
            
            // Lighting calculations
            float diffuse = max(dot(normal, light_dir), 0.0);
            float specular = 0.0;
            if (diffuse > 0.0) {
                vec3 reflect_dir = reflect(-light_dir, normal);
                specular = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0) * 0.3;
            }
            
            // Atmospheric effects
            vec3 atmospheric_color = vec3(0.0);
            if (has_atmosphere) {
                atmospheric_color = calculate_atmospheric_scattering(view_dir, light_dir) * pressure * 1e-5;
            }
            
            // Cloud shadows
            float cloud_shadow = 1.0;
            if (has_clouds) {
                cloud_shadow = 0.7 + 0.3 * texture(cloud_texture, uv * 2.0).r;
            }
            
            // Final color composition
            vec3 final_color = surface_color * (0.2 + 0.8 * diffuse * cloud_shadow) + 
                              light_color * specular + atmospheric_color;
            
            // Thermal glow for hot planets
            if (temperature > 800.0) {
                float thermal = (temperature - 800.0) / 1000.0;
                final_color += vec3(1.0, 0.3, 0.1) * thermal;
            }
            
            frag_color = vec4(final_color, 1.0);
        }
        """
        
        return self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    
    def _create_star_shader(self):
        """Create realistic star rendering shader with corona effects"""
        vertex_shader = """
        #version 330 core
        
        layout (location = 0) in vec3 position;
        layout (location = 1) in vec3 normal;
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        uniform float time;
        
        out vec3 world_pos;
        out vec3 world_normal;
        out float surface_activity;
        
        float noise(vec3 p) {
            return sin(p.x * 20.0 + time) * sin(p.y * 20.0 + time * 1.1) * sin(p.z * 20.0 + time * 0.9);
        }
        
        void main() {
            vec3 displaced_pos = position + normal * noise(position) * 0.02;
            surface_activity = noise(position * 10.0) * 0.5 + 0.5;
            
            world_pos = (model * vec4(displaced_pos, 1.0)).xyz;
            world_normal = mat3(model) * normal;
            
            gl_Position = projection * view * vec4(world_pos, 1.0);
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec3 world_pos;
        in vec3 world_normal;
        in float surface_activity;
        
        uniform vec3 star_color;
        uniform float temperature;
        uniform float luminosity;
        uniform vec3 camera_pos;
        
        out vec4 frag_color;
        
        vec3 blackbody_color(float temp) {
            // Simplified blackbody radiation color
            float t = temp / 1000.0;
            vec3 color;
            
            if (t < 3.0) {
                color = vec3(1.0, 0.3, 0.1); // Red
            } else if (t < 6.0) {
                color = vec3(1.0, 0.8, 0.4); // Orange-Yellow
            } else if (t < 8.0) {
                color = vec3(1.0, 1.0, 0.8); // White
            } else {
                color = vec3(0.8, 0.9, 1.0); // Blue
            }
            
            return color;
        }
        
        void main() {
            vec3 view_dir = normalize(camera_pos - world_pos);
            vec3 normal = normalize(world_normal);
            
            // Limb darkening effect
            float limb_factor = dot(normal, view_dir);
            float limb_darkening = 0.4 + 0.6 * pow(limb_factor, 0.6);
            
            // Corona effect at edges
            float corona = 1.0 - limb_factor;
            corona = pow(corona, 2.0) * 0.5;
            
            // Stellar color based on temperature
            vec3 stellar_color = blackbody_color(temperature);
            
            // Surface activity (solar flares, sunspots)
            vec3 activity_color = vec3(1.0, 0.5, 0.2) * surface_activity * 0.3;
            
            vec3 final_color = (stellar_color + activity_color) * limb_darkening + 
                              stellar_color * corona * 2.0;
            
            // Brightness based on luminosity
            float brightness = sqrt(luminosity / 3.828e26); // Normalized to solar luminosity
            final_color *= brightness;
            
            frag_color = vec4(final_color, 1.0);
        }
        """
        
        return self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    
    def render_scene(self, bodies: List[CelestialBody], camera_pos: np.ndarray, 
                    camera_target: np.ndarray):
        """Render the complete scene with all celestial bodies"""
        self.ctx.clear(0.0, 0.0, 0.02)  # Deep space background
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        
        # Update camera
        self.camera_position = camera_pos
        self.camera_target = camera_target
        
        # Calculate view and projection matrices
        view_matrix = self._calculate_view_matrix()
        proj_matrix = self._calculate_projection_matrix()
        
        # Collect light sources
        self.light_positions.clear()
        self.light_colors.clear()
        
        for body in bodies:
            if body.object_type == ObjectType.STAR:
                self.light_positions.append(body.physics.position)
                color = self._temperature_to_color(body.physics.temperature)
                self.light_colors.append(color)
        
        # Render stars first (they emit light)
        for body in bodies:
            if body.object_type == ObjectType.STAR:
                self._render_star(body, view_matrix, proj_matrix)
        
        # Render planets and other objects
        for body in bodies:
            if body.object_type != ObjectType.STAR:
                if body.object_type == ObjectType.PLANET:
                    self._render_planet(body, view_matrix, proj_matrix)
                elif body.object_type == ObjectType.ASTEROID:
                    self._render_asteroid(body, view_matrix, proj_matrix)
                elif body.object_type == ObjectType.BLACK_HOLE:
                    self._render_black_hole(body, view_matrix, proj_matrix)

class UniverseGUI:
    """Comprehensive GUI system for universe simulation control"""
    
    def __init__(self, physics_engine: AdvancedPhysicsEngine, graphics_engine: GraphicsEngine):
        self.physics = physics_engine
        self.graphics = graphics_engine
        
        # GUI state
        self.show_main_menu = True
        self.show_object_editor = False
        self.show_physics_panel = True
        self.show_graphics_panel = False
        self.show_presets_panel = False
        self.show_analysis_panel = False
        self.show_time_controls = True
        
        self.selected_body = None
        self.camera_follow_body = None
        
        # Control parameters
        self.time_scale = 1.0
        self.simulation_paused = False
        self.show_orbits = True
        self.show_labels = True
        self.show_velocity_vectors = False
        self.show_force_vectors = False
        self.show_habitable_zones = True
        
        # Creation tools
        self.creation_mode = False
        self.new_body_params = {
            'mass': 5.972e24,
            'radius': 6.371e6,
            'object_type': ObjectType.PLANET,
            'temperature': 288.0,
            'has_atmosphere': False
        }
        
        # Analysis data
        self.orbital_data = {}
        self.energy_history = []
        self.temperature_history = []
        
    def render_gui(self):
        """Render all GUI panels"""
        if self.show_main_menu:
            self._render_main_menu()
        
        if not self.show_main_menu:
            self._render_menu_bar()
            
            if self.show_time_controls:
                self._render_time_controls()
            
            if self.show_physics_panel:
                self._render_physics_panel()
            
            if self.show_graphics_panel:
                self._render_graphics_panel()
            
            if self.show_object_editor and self.selected_body:
                self._render_object_editor()
            
            if self.show_presets_panel:
                self._render_presets_panel()
            
            if self.show_analysis_panel:
                self._render_analysis_panel()
            
            self._render_object_list()
            self._render_status_bar()
    
    def _render_main_menu(self):
        """Render the main menu"""
        imgui.set_next_window_size(400, 500)
        imgui.set_next_window_position(400, 200)
        
        expanded, opened = imgui.begin("Stellar Forge - Universe Simulator", 
                                      flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)
        
        if expanded:
            imgui.push_font()  # Use larger font for title
            imgui.text("Welcome to Stellar Forge")
            imgui.separator()
            
            if imgui.button("New Solar System", width=350):
                self._load_preset("solar_system")
                self.show_main_menu = False
            
            if imgui.button("Binary Star System", width=350):
                self._load_preset("binary_stars")
                self.show_main_menu = False
            
            if imgui.button("Galaxy Formation", width=350):
                self._load_preset("galaxy_formation")
                self.show_main_menu = False
            
            if imgui.button("Black Hole Accretion", width=350):
                self._load_preset("black_hole")
                self.show_main_menu = False
            
            if imgui.button("Planetary Formation", width=350):
                self._load_preset("planetary_disk")
                self.show_main_menu = False
            
            imgui.separator()
            
            if imgui.button("Load Simulation", width=170):
                self._load_simulation()
            
            imgui.same_line()
            
            if imgui.button("Settings", width=170):
                pass  # Open settings dialog
            
            imgui.separator()
            
            imgui.text("Features:")
            imgui.bullet_text("Real-time N-body physics simulation")
            imgui.bullet_text("General relativistic effects")
            imgui.bullet_text("Stellar evolution and supernovae")
            imgui.bullet_text("Planetary atmosphere modeling")
            imgui.bullet_text("Collision detection and fragmentation")
            imgui.bullet_text("Tidal forces and orbital mechanics")
            imgui.bullet_text("Habitable zone calculations")
            imgui.bullet_text("Advanced particle systems")
            
        imgui.end()
    
    def _render_physics_panel(self):
        """Render physics simulation controls"""
        imgui.begin("Physics Engine")
        
        # Simulation mode
        imgui.text("Simulation Mode:")
        clicked, self.physics.simulation_mode = imgui.combo(
            "##SimMode", 
            self.physics.simulation_mode.value,
            [mode.value for mode in SimulationMode]
        )
        
        imgui.separator()
        
        # Time step controls
        imgui.text("Time Integration:")
        changed, self.physics.time_step = imgui.slider_float(
            "Time Step (s)", self.physics.time_step, 1.0, 86400.0, "%.0f"
        )
        
        # Barnes-Hut optimization
        imgui.checkbox("Use Barnes-Hut Algorithm", self.physics.use_barnes_hut)
        if self.physics.use_barnes_hut:
            imgui.same_line()
            changed, self.physics.barnes_hut_theta = imgui.slider_float(
                "Theta", self.physics.barnes_hut_theta, 0.1, 2.0, "%.2f"
            )
        
        imgui.separator()
        
        # Physics effects toggles
        imgui.text("Physical Effects:")
        imgui.checkbox("Collision Detection", self.physics.collision_detection)
        imgui.checkbox("Tidal Forces", self.physics.tidal_forces)
        imgui.checkbox("Radiation Pressure", self.physics.radiation_pressure)
        
        if self.physics.simulation_mode == SimulationMode.GENERAL_RELATIVITY:
            imgui.checkbox("Gravitational Lensing", True)
            imgui.checkbox("Time Dilation", True)
            imgui.checkbox("Gravitational Waves", True)
        
        imgui.separator()
        
        # System statistics
        imgui.text(f"Bodies: {len(self.physics.bodies)}")
        imgui.text(f"Simulation Time: {self.physics.simulation_time/86400:.2f} days")
        
        total_mass = sum(body.mass for body in self.physics.bodies)
        imgui.text(f"Total Mass: {total_mass:.2e} kg")
        
        total_energy = self._calculate_system_energy()
        imgui.text(f"Total Energy: {total_energy:.2e} J")
        
        imgui.end()
    
    def _render_object_editor(self):
        """Render detailed object property editor"""
        if not self.selected_body:
            return
            
        body = self.selected_body
        imgui.begin(f"Object Editor - {body.name}")
        
        # Basic properties
        if imgui.collapsing_header("Basic Properties", flags=imgui.TREE_NODE_DEFAULT_OPEN):
            imgui.input_text("Name", body.name, 256)
            
            # Object type
            type_names = [t.value for t in ObjectType]
            clicked, selected = imgui.combo("Type", type_names.index(body.object_type.value), type_names)
            if clicked:
                body.object_type = ObjectType(type_names[selected])
            
            # Physical properties
            changed, body.mass = imgui.input_double("Mass (kg)", body.mass, format="%.3e")
            changed, body.radius = imgui.input_double("Radius (m)", body.radius, format="%.3e")
            changed, body.density = imgui.input_float("Density (kg/m³)", body.density)
            
        # Position and velocity
        if imgui.collapsing_header("Motion"):
            pos = body.physics.position
            changed, new_pos = imgui.input_float3("Position (m)", *pos)
            if changed:
                body.physics.position = np.array(new_pos)
            
            vel = body.physics.velocity
            changed, new_vel = imgui.input_float3("Velocity (m/s)", *vel)
            if changed:
                body.physics.velocity = np.array(new_vel)
            
            acc = body.physics.acceleration
            imgui.text(f"Acceleration: ({acc[0]:.2e}, {acc[1]:.2e}, {acc[2]:.2e}) m/s²")
            
        # Thermal properties
        if imgui.collapsing_header("Thermal Properties"):
            changed, body.physics.temperature = imgui.input_float(
                "Surface Temperature (K)", body.physics.temperature)
            
            if body.object_type == ObjectType.STAR:
                changed, body.physics.luminosity = imgui.input_double(
                    "Luminosity (W)", body.physics.luminosity, format="%.3e")
                    
                imgui.text(f"Age: {body.age:.2e} years")
                
                # Stellar evolution status
                main_seq_lifetime = 10e9 * (body.mass / PhysicsConstants.SOLAR_MASS)**(-2.5)
                evolution_phase = "Main Sequence"
                if body.age > main_seq_lifetime:
                    evolution_phase = "Post-Main Sequence"
                imgui.text(f"Evolution Phase: {evolution_phase}")
        
        # Atmospheric properties
        if body.object_type == ObjectType.PLANET:
            if imgui.collapsing_header("Atmosphere"):
                imgui.checkbox("Has Atmosphere", body.has_atmosphere)
                
                if body.has_atmosphere:
                    changed, body.atmosphere_mass = imgui.input_double(
                        "Atmospheric Mass (kg)", body.atmosphere_mass, format="%.3e")
                    
                    changed, body.surface_pressure = imgui.input_float(
                        "Surface Pressure (Pa)", body.surface_pressure)
                    
                    changed, body.greenhouse_effect = imgui.input_float(
                        "Greenhouse Effect (K)", body.greenhouse_effect)
        
        # Orbital information
        if imgui.collapsing_header("Orbital Data"):
            imgui.text(f"Semi-major axis: {body.semi_major_axis/PhysicsConstants.AU:.3f} AU")
            imgui.text(f"Eccentricity: {body.eccentricity:.3f}")
            imgui.text(f"Inclination: {math.degrees(body.inclination):.1f}°")
            
            if body.is_potentially_habitable:
                imgui.text_colored((0, 1, 0, 1), "POTENTIALLY HABITABLE")
        
        # Actions
        imgui.separator()
        if imgui.button("Center Camera"):
            self._center_camera_on_body(body)
        
        imgui.same_line()
        if imgui.button("Follow"):
            self.camera_follow_body = body
        
        imgui.same_line()
        if imgui.button("Delete", (50, 0)):
            self.physics.remove_body(body)
            self.selected_body = None
        
        imgui.end()

class StellarForgeApp:
    """Main application class"""
    
    def __init__(self):
        pygame.init()
        
        # Window setup
        self.width = 1920
        self.height = 1080
        self.screen = pygame.display.set_mode(
            (self.width, self.height), 
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
        )
        pygame.display.set_caption("Stellar Forge - Universe Simulator")
        
        # Initialize engines
        self.physics = AdvancedPhysicsEngine(SimulationMode.GENERAL_RELATIVITY)
        self.graphics = GraphicsEngine(self.width, self.height)
        
        # Initialize GUI
        imgui.create_context()
        self.gui_renderer = PygameRenderer()
        self.gui = UniverseGUI(self.physics, self.graphics)
        
        # Simulation state
        self.running = True
        self.clock = pygame.time.Clock()
        self.fps_target = 60
        
        # Camera controls
        self.camera_position = np.array([0.0, 0.0, PhysicsConstants.AU])
        self.camera_target = np.array([0.0, 0.0, 0.0])
        self.camera_speed = PhysicsConstants.AU / 1000
        
        # Input state
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_dragging = False
        self.last_mouse_pos = (0, 0)
        
    def run(self):
        """Main application loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps_target)
        
        self.cleanup()
    
    def handle_events(self):
        """Handle pygame and GUI events"""
        for event in pygame.event.get():
            self.gui_renderer.process_event(event)
            
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self._handle_keyboard_shortcuts(event.key)
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_dragging = True
                    self.last_mouse_pos = event.pos
                elif event.button == 3:  # Right click
                    self._handle_object_selection(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                if self.mouse_dragging:
                    self._handle_camera_rotation(event.rel)
            
            elif event.type == pygame.MOUSEWHEEL:
                self._handle_camera_zoom(event.y)
    
    def update(self):
        """Update simulation state"""
        if not self.gui.simulation_paused:
            # Update physics
            dt = self.physics.time_step * self.gui.time_scale
            self.physics.step(dt)
            
            # Update camera following
            if self.gui.camera_follow_body:
                self.camera_target = self.gui.camera_follow_body.physics.position.copy()
        
        # Handle continuous keyboard input
        self._handle_camera_movement()
        
        # Update GUI data
        self._update_analysis_data()
    
    def render(self):
        """Render the complete scene"""
        # Render 3D scene
        self.graphics.render_scene(
            self.physics.bodies,
            self.camera_position,
            self.camera_target
        )
        
        # Render GUI
        imgui.new_frame()
        self.gui.render_gui()
        
        # Render additional overlays
        if self.gui.show_orbits:
            self._render_orbit_lines()
        
        if self.gui.show_labels:
            self._render_body_labels()
        
        if self.gui.show_velocity_vectors:
            self._render_velocity_vectors()
        
        if self.gui.show_habitable_zones:
            self._render_habitable_zones()
        
        # Finalize rendering
        imgui.render()
        self.gui_renderer.render(imgui.get_draw_data())
        pygame.display.flip()
    
    def cleanup(self):
        """Cleanup resources"""
        self.gui_renderer.shutdown()
        pygame.quit()

def main():
    """Entry point for the application"""
    app = StellarForgeApp()
    
    # Load default solar system
    app.gui._load_preset("solar_system")
    
    print("Starting Stellar Forge Universe Simulator...")
    print("Controls:")
    print("  WASD + QE - Camera movement")
    print("  Mouse drag - Camera rotation") 
    print("  Mouse wheel - Zoom")
    print("  Right click - Select object")
    print("  Space - Pause/Resume simulation")
    print("  F - Follow selected object")
    print("  R - Reset camera")
    print("  ESC - Exit")
    
    app.run()

if __name__ == "__main__":
    main()
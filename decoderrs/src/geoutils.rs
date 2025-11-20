
use nalgebra::{Matrix3, Vector3};
use serde::Serialize;

pub const A: f64 = 6378137.0;
pub const B: f64 = 6356752.3142;
pub const E2: f64 = 0.00669437999013;

#[derive(Debug, Clone, Copy, Serialize)]
pub struct CoordinatesWGS84 {
    pub lat: f64,
    pub lon: f64,
    pub height: f64,
}

#[derive(Debug, Clone, Copy, Serialize)]
pub struct CoordinatesXYZ {
    pub x: f64,
    pub y: f64,
    pub z: f64,
}

#[derive(Debug, Clone, Copy, Serialize)]
pub struct CoordinatesPolar {
    pub rho: f64,
    pub theta: f64,
    pub elevation: f64,
}

pub fn change_geocentric_2_geodesic(c: &CoordinatesXYZ) -> CoordinatesWGS84 {
    let mut res = CoordinatesWGS84 {
        lat: 0.0,
        lon: 0.0,
        height: 0.0,
    };
    if c.x.abs() < 1e-10 && c.y.abs() < 1e-10 {
        if c.z.abs() < 1e-10 {
            res.lat = std::f64::consts::PI / 2.0;
        } else {
            let sign_z = if c.z > 0.0 { 1.0 } else { -1.0 };
            res.lat = (std::f64::consts::PI / 2.0) * (sign_z + 0.5);
        }
        res.lon = 0.0;
        res.height = c.z.abs() - B;
        return res;
    }

    let d_xy = (c.x.powi(2) + c.y.powi(2)).sqrt();
    let p = ((c.z / d_xy) / (1.0 - (A * E2) / (d_xy.powi(2) + c.z.powi(2)).sqrt())).atan();
    res.lat = p;
    let sin_p = p.sin();
    let nu = A / (1.0 - E2 * sin_p.powi(2)).sqrt();
    let cos_p = p.cos();
    res.height = (d_xy / cos_p) - nu;
    let mut lat_over = p;
    let mut loop_count = 0;
    while (res.lat - lat_over).abs() > 1e-8 && loop_count < 50 {
        loop_count += 1;
        lat_over = res.lat;
        let sin_lat = res.lat.sin();
        let nu = A / (1.0 - E2 * sin_lat.powi(2)).sqrt();
        res.lat = ((c.z + res.height) / nu / (d_xy * (1.0 - E2 + res.height / nu))).atan();
        let cos_lat = res.lat.cos();
        res.height = d_xy / cos_lat - nu;
    }
    res.lon = c.y.atan2(c.x);
    res
}

pub fn calculate_rotation_matrix(lat: f64, lon: f64) -> Matrix3<f64> {
    let sin_lon = lon.sin();
    let cos_lon = lon.cos();
    let sin_lat = lat.sin();
    let cos_lat = lat.cos();
    Matrix3::new(
        -sin_lon, cos_lon, 0.0,
        -sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat,
        cos_lat * cos_lon, cos_lat * sin_lon, sin_lat,
    )
}

pub fn calculate_translation_matrix(c: &CoordinatesWGS84) -> Vector3<f64> {
    let sin_lat = c.lat.sin();
    let nu = A / (1.0 - E2 * sin_lat.powi(2)).sqrt();
    let cos_lat = c.lat.cos();
    let cos_lon = c.lon.cos();
    let sin_lon = c.lon.sin();

    Vector3::new(
        (nu + c.height) * cos_lat * cos_lon,
        (nu + c.height) * cos_lat * sin_lon,
        (nu * (1.0 - E2) + c.height) * sin_lat,
    )
}

pub fn change_radar_spherical_2_radar_cartesian(polar: &CoordinatesPolar) -> CoordinatesXYZ {
    let cos_el = polar.elevation.cos();
    let sin_theta = polar.theta.sin();
    let cos_theta = polar.theta.cos();
    CoordinatesXYZ {
        x: polar.rho * cos_el * sin_theta,
        y: polar.rho * cos_el * cos_theta,
        z: polar.rho * polar.elevation.sin(),
    }
}

pub fn change_radar_cartesian_2_geocentric(
    radar_coordinates: &CoordinatesWGS84,
    cartesian_coordinates: &CoordinatesXYZ,
) -> CoordinatesXYZ {
    let translation_matrix = calculate_translation_matrix(radar_coordinates);
    let rotation_matrix = calculate_rotation_matrix(radar_coordinates.lat, radar_coordinates.lon);

    let input_vec = Vector3::new(cartesian_coordinates.x, cartesian_coordinates.y, cartesian_coordinates.z);
    
    let r1 = rotation_matrix.transpose() * input_vec;
    let r2 = r1 + translation_matrix;
    
    CoordinatesXYZ {
        x: r2.x,
        y: r2.y,
        z: r2.z,
    }
}

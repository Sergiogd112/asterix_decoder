using System;
using System.Collections.Generic;

namespace PGTA_deco048;

public class GeoUtils
{
	public static readonly object PositionRadarMatrixLock = new object();

	public static readonly object RotationRadarMatrixLock = new object();

	public const double METERS2FEET = 3.28084;

	public const double FEET2METERS = 0.3048;

	public const double METERS2NM = 0.0005399568034557236;

	public const double NM2METERS = 1852.0;

	public const double DEGS2RADS = Math.PI / 180.0;

	public const double RADS2DEGS = 180.0 / Math.PI;

	public double A = 6378137.0;

	public double B = 6356752.314245;

	public double E2 = 0.00669437999013;

	public const double ALMOST_ZERO = 1E-10;

	public const double REQUIERED_PRECISION = 1E-08;

	public CoordinatesWGS84 centerProjection;

	private GeneralMatrix T1;

	private GeneralMatrix R1;

	public double R_S;

	private Dictionary<CoordinatesWGS84, GeneralMatrix> rotationMatrixHT;

	private Dictionary<CoordinatesWGS84, GeneralMatrix> translationMatrixHT;

	private Dictionary<CoordinatesWGS84, GeneralMatrix> positionRadarMatrixHT;

	private Dictionary<CoordinatesWGS84, GeneralMatrix> rotationRadarMatrixHT;

	public GeoUtils()
	{
	}

	public GeoUtils(double E, double A)
	{
		E2 = E * E;
		this.A = A;
		setCenterProjection(new CoordinatesWGS84());
	}

	public GeoUtils(double E, double A, CoordinatesWGS84 centerProjection)
	{
		E2 = E * E;
		this.A = A;
		setCenterProjection(centerProjection);
	}

	public static double LatLon2Degrees(double d1, double d2, double d3, int ns)
	{
		double num = d1 + d2 / 60.0 + d3 / 3600.0;
		if (ns == 1)
		{
			num *= -1.0;
		}
		return num;
	}

	public static double LatLon2Radians(double d1, double d2, double d3, int ns)
	{
		double num = d1 + d2 / 60.0 + d3 / 3600.0;
		if (ns == 1)
		{
			num *= -1.0;
		}
		return num * (Math.PI / 180.0);
	}

	public static double LatLonString2Degrees(string s1, string s2, string s3, int ns)
	{
		double result = 0.0;
		try
		{
			double d = double.Parse(s1);
			double d2 = double.Parse(s2);
			double d3 = double.Parse(s3);
			result = LatLon2Degrees(d, d2, d3, ns);
		}
		catch (FormatException)
		{
		}
		return result;
	}

	public static void Degrees2LatLon(double d, out double d1, out double d2, out double d3, out int ns)
	{
		if (d < 0.0)
		{
			d *= -1.0;
			ns = 1;
		}
		else
		{
			ns = 0;
		}
		d1 = Math.Floor(d);
		d2 = Math.Floor((d - d1) * 60.0);
		d3 = ((d - d1) * 60.0 - d2) * 60.0;
	}

	public static void Radians2LatLon(double d, out double d1, out double d2, out double d3, out int ns)
	{
		d *= 180.0 / Math.PI;
		if (d < 0.0)
		{
			d *= -1.0;
			ns = 1;
		}
		else
		{
			ns = 0;
		}
		d1 = Math.Floor(d);
		d2 = Math.Floor((d - d1) * 60.0);
		d3 = ((d - d1) * 60.0 - d2) * 60.0;
	}

	public static CoordinatesWGS84 CenterCoordinates(List<CoordinatesWGS84> l)
	{
		double num = -999.0;
		double num2 = -999.0;
		double num3 = 999.0;
		double num4 = 999.0;
		double num5 = -999.0;
		if (l != null && l.Count > 0)
		{
			foreach (CoordinatesWGS84 item in l)
			{
				if (num < item.Lat)
				{
					num = item.Lat;
				}
				if (num2 < item.Lon)
				{
					num2 = item.Lon;
				}
				if (num3 > item.Lat)
				{
					num3 = item.Lat;
				}
				if (num4 > item.Lon)
				{
					num4 = item.Lon;
				}
				if (num5 < item.Height)
				{
					num5 = item.Height;
				}
			}
			return new CoordinatesWGS84
			{
				Lat = (num + num3) / 2.0,
				Lon = (num2 + num4) / 2.0,
				Height = num5
			};
		}
		return null;
	}

	public CoordinatesXYZ change_geodesic2geocentric(CoordinatesWGS84 c)
	{
		if (c == null)
		{
			return null;
		}
		CoordinatesXYZ coordinatesXYZ = new CoordinatesXYZ();
		double num = A / Math.Sqrt(1.0 - E2 * Math.Pow(Math.Sin(c.Lat), 2.0));
		coordinatesXYZ.X = (num + c.Height) * Math.Cos(c.Lat) * Math.Cos(c.Lon);
		coordinatesXYZ.Y = (num + c.Height) * Math.Cos(c.Lat) * Math.Sin(c.Lon);
		coordinatesXYZ.Z = (num * (1.0 - E2) + c.Height) * Math.Sin(c.Lat);
		return coordinatesXYZ;
	}

	public CoordinatesWGS84 change_geocentric2geodesic(CoordinatesXYZ c)
	{
		if (c == null)
		{
			return null;
		}
		CoordinatesWGS84 coordinatesWGS = new CoordinatesWGS84();
		double num = 6356752.314245;
		if (Math.Abs(c.X) < 1E-10 && Math.Abs(c.Y) < 1E-10)
		{
			if (Math.Abs(c.Z) < 1E-10)
			{
				coordinatesWGS.Lat = Math.PI / 2.0;
			}
			else
			{
				coordinatesWGS.Lat = Math.PI / 2.0 * (c.Z / Math.Abs(c.Z) + 0.5);
			}
			coordinatesWGS.Lon = 0.0;
			coordinatesWGS.Height = Math.Abs(c.Z) - num;
			return coordinatesWGS;
		}
		double num2 = Math.Sqrt(c.X * c.X + c.Y * c.Y);
		coordinatesWGS.Lat = Math.Atan(c.Z / num2 / (1.0 - A * E2 / Math.Sqrt(num2 * num2 + c.Z * c.Z)));
		double num3 = A / Math.Sqrt(1.0 - E2 * Math.Pow(Math.Sin(coordinatesWGS.Lat), 2.0));
		coordinatesWGS.Height = num2 / Math.Cos(coordinatesWGS.Lat) - num3;
		double num4 = ((!(coordinatesWGS.Lat >= 0.0)) ? 0.1 : (-0.1));
		int num5 = 0;
		while (Math.Abs(coordinatesWGS.Lat - num4) > 1E-08 && num5 < 50)
		{
			num5++;
			num4 = coordinatesWGS.Lat;
			coordinatesWGS.Lat = Math.Atan(c.Z * (1.0 + coordinatesWGS.Height / num3) / (num2 * (1.0 - E2 + coordinatesWGS.Height / num3)));
			num3 = A / Math.Sqrt(1.0 - E2 * Math.Pow(Math.Sin(coordinatesWGS.Lat), 2.0));
			coordinatesWGS.Height = num2 / Math.Cos(coordinatesWGS.Lat) - num3;
		}
		coordinatesWGS.Lon = Math.Atan2(c.Y, c.X);
		return coordinatesWGS;
	}

	public CoordinatesWGS84 setCenterProjection(CoordinatesWGS84 c)
	{
		if (c == null)
		{
			return null;
		}
		CoordinatesWGS84 coordinatesWGS = (centerProjection = new CoordinatesWGS84(c.Lat, c.Lon, 0.0));
		_ = A / Math.Sqrt(1.0 - E2 * Math.Pow(Math.Sin(coordinatesWGS.Lat), 2.0));
		R_S = A * (1.0 - E2) / Math.Pow(1.0 - E2 * Math.Pow(Math.Sin(coordinatesWGS.Lat), 2.0), 1.5);
		T1 = CalculateTranslationMatrix(coordinatesWGS, A, E2);
		R1 = CalculateRotationMatrix(coordinatesWGS.Lat, coordinatesWGS.Lon);
		return centerProjection;
	}

	public CoordinatesWGS84 getCenterProjection()
	{
		return centerProjection;
	}

	public CoordinatesXYZ change_geocentric2system_cartesian(CoordinatesXYZ geo)
	{
		if (centerProjection == null || R1 == null || T1 == null || geo == null)
		{
			return null;
		}
		double[][] obj = new double[3][]
		{
			new double[1],
			new double[1],
			new double[1]
		};
		obj[0][0] = geo.X;
		obj[1][0] = geo.Y;
		obj[2][0] = geo.Z;
		GeneralMatrix generalMatrix = new GeneralMatrix(obj, 3, 1);
		generalMatrix.SubtractEquals(T1);
		GeneralMatrix generalMatrix2 = R1.Multiply(generalMatrix);
		return new CoordinatesXYZ(generalMatrix2.GetElement(0, 0), generalMatrix2.GetElement(1, 0), generalMatrix2.GetElement(2, 0));
	}

	public CoordinatesXYZ change_system_cartesian2geocentric(CoordinatesXYZ car)
	{
		if (car == null)
		{
			return null;
		}
		double[][] obj = new double[3][]
		{
			new double[1],
			new double[1],
			new double[1]
		};
		obj[0][0] = car.X;
		obj[1][0] = car.Y;
		obj[2][0] = car.Z;
		GeneralMatrix b = new GeneralMatrix(obj, 3, 1);
		GeneralMatrix generalMatrix = R1.Transpose().Multiply(b);
		generalMatrix.AddEquals(T1);
		return new CoordinatesXYZ(generalMatrix.GetElement(0, 0), generalMatrix.GetElement(1, 0), generalMatrix.GetElement(2, 0));
	}

	public double change_system_xyh2system_z(CoordinatesXYH c)
	{
		double num = 0.0;
		if (c == null)
		{
			return 0.0;
		}
		double num2 = c.X / (R_S + c.Height);
		double num3 = c.Y / (R_S + c.Height);
		double num4 = num2 * num2 + num3 * num3;
		if (num4 > 1.0)
		{
			return 0.0 - (R_S + centerProjection.Height);
		}
		return (R_S + c.Height) * Math.Sqrt(1.0 - num4) - (R_S + centerProjection.Height);
	}

	public CoordinatesUVH change_system_cartesian2stereographic(CoordinatesXYZ c)
	{
		if (c == null)
		{
			return null;
		}
		CoordinatesUVH coordinatesUVH = new CoordinatesUVH();
		double num = c.X * c.X + c.Y * c.Y;
		coordinatesUVH.Height = Math.Sqrt(num + (c.Z + centerProjection.Height + R_S) * (c.Z + centerProjection.Height + R_S)) - R_S;
		double num2 = 2.0 * R_S / (2.0 * R_S + centerProjection.Height + c.Z + coordinatesUVH.Height);
		coordinatesUVH.U = num2 * c.X;
		coordinatesUVH.V = num2 * c.Y;
		return coordinatesUVH;
	}

	public CoordinatesXYZ change_stereographic2system_cartesian(CoordinatesUVH c)
	{
		if (c == null)
		{
			return null;
		}
		CoordinatesXYZ coordinatesXYZ = new CoordinatesXYZ();
		double num = c.U * c.U + c.V * c.V;
		coordinatesXYZ.Z = (c.Height + R_S) * ((4.0 * R_S * R_S - num) / (4.0 * R_S * R_S + num)) - (R_S + centerProjection.Height);
		double num2 = 2.0 * R_S / (2.0 * R_S + centerProjection.Height + coordinatesXYZ.Z + c.Height);
		coordinatesXYZ.X = c.U / num2;
		coordinatesXYZ.Y = c.V / num2;
		return coordinatesXYZ;
	}

	public static double CalculateElevation(CoordinatesWGS84 centerCoordinates, double R, double rho, double h)
	{
		if (rho < 1E-10 || R == -1.0 || centerCoordinates == null)
		{
			return 0.0;
		}
		double num = (2.0 * R * (h - centerCoordinates.Height) + h * h - centerCoordinates.Height * centerCoordinates.Height - rho * rho) / (2.0 * rho * (R + centerCoordinates.Height));
		if (num > -1.0 && num < 1.0)
		{
			return Math.Asin(num);
		}
		return Math.PI / 2.0;
	}

	public static double CalculateAzimuth(double x, double y)
	{
		double num = ((!(Math.Abs(y) < 1E-10)) ? Math.Atan2(x, y) : (x / Math.Abs(x) * Math.PI / 2.0));
		if (num < 0.0)
		{
			num += Math.PI * 2.0;
		}
		return num;
	}

	public double CalculateEarthRadius(CoordinatesWGS84 geo)
	{
		double result = double.NaN;
		if (geo != null)
		{
			result = A * (1.0 - E2) / Math.Pow(1.0 - E2 * Math.Pow(Math.Sin(geo.Lat), 2.0), 1.5);
		}
		return result;
	}

	public static GeneralMatrix CalculateRotationMatrix(double lat, double lon)
	{
		double[][] obj = new double[3][]
		{
			new double[3],
			new double[3],
			new double[3]
		};
		obj[0][0] = 0.0 - Math.Sin(lon);
		obj[0][1] = Math.Cos(lon);
		obj[0][2] = 0.0;
		obj[1][0] = 0.0 - Math.Sin(lat) * Math.Cos(lon);
		obj[1][1] = 0.0 - Math.Sin(lat) * Math.Sin(lon);
		obj[1][2] = Math.Cos(lat);
		obj[2][0] = Math.Cos(lat) * Math.Cos(lon);
		obj[2][1] = Math.Cos(lat) * Math.Sin(lon);
		obj[2][2] = Math.Sin(lat);
		return new GeneralMatrix(obj, 3, 3);
	}

	public static GeneralMatrix CalculateTranslationMatrix(CoordinatesWGS84 c, double A, double E2)
	{
		double num = A / Math.Sqrt(1.0 - E2 * Math.Pow(Math.Sin(c.Lat), 2.0));
		double[][] obj = new double[3][]
		{
			new double[1],
			new double[1],
			new double[1]
		};
		obj[0][0] = (num + c.Height) * Math.Cos(c.Lat) * Math.Cos(c.Lon);
		obj[1][0] = (num + c.Height) * Math.Cos(c.Lat) * Math.Sin(c.Lon);
		obj[2][0] = (num * (1.0 - E2) + c.Height) * Math.Sin(c.Lat);
		return new GeneralMatrix(obj, 3, 1);
	}

	public static GeneralMatrix CalculatePositionRadarMatrix(GeneralMatrix T1, GeneralMatrix t, GeneralMatrix r)
	{
		GeneralMatrix b = T1.Subtract(t);
		return r.Multiply(b);
	}

	public static GeneralMatrix CalculateRotationRadarMatrix(GeneralMatrix R1, GeneralMatrix r)
	{
		GeneralMatrix b = R1.Transpose();
		return r.Multiply(b);
	}

	public CoordinatesXYZ change_radar_spherical2radar_cartesian(CoordinatesPolar polarCoordinates)
	{
		if (polarCoordinates == null)
		{
			return null;
		}
		return new CoordinatesXYZ
		{
			X = polarCoordinates.Rho * Math.Cos(polarCoordinates.Elevation) * Math.Sin(polarCoordinates.Theta),
			Y = polarCoordinates.Rho * Math.Cos(polarCoordinates.Elevation) * Math.Cos(polarCoordinates.Theta),
			Z = polarCoordinates.Rho * Math.Sin(polarCoordinates.Elevation)
		};
	}

	public CoordinatesXYZ change_radar_cartesian2geocentric(CoordinatesWGS84 radarCoordinates, CoordinatesXYZ cartesianCoordinates)
	{
		GeneralMatrix b = ObtainTranslationMatrix(radarCoordinates);
		GeneralMatrix generalMatrix = ObtainRotationMatrix(radarCoordinates);
		double[][] obj = new double[3][]
		{
			new double[1],
			new double[1],
			new double[1]
		};
		obj[0][0] = cartesianCoordinates.X;
		obj[1][0] = cartesianCoordinates.Y;
		obj[2][0] = cartesianCoordinates.Z;
		GeneralMatrix b2 = new GeneralMatrix(obj, 3, 1);
		GeneralMatrix generalMatrix2 = generalMatrix.Transpose().Multiply(b2);
		generalMatrix2.AddEquals(b);
		return new CoordinatesXYZ(generalMatrix2.GetElement(0, 0), generalMatrix2.GetElement(1, 0), generalMatrix2.GetElement(2, 0));
	}

	private GeneralMatrix ObtainRotationMatrix(CoordinatesWGS84 radarCoordinates)
	{
		GeneralMatrix generalMatrix = null;
		if (rotationMatrixHT == null)
		{
			rotationMatrixHT = new Dictionary<CoordinatesWGS84, GeneralMatrix>(16);
		}
		if (rotationMatrixHT.ContainsKey(radarCoordinates))
		{
			generalMatrix = rotationMatrixHT[radarCoordinates];
		}
		else
		{
			generalMatrix = CalculateRotationMatrix(radarCoordinates.Lat, radarCoordinates.Lon);
			rotationMatrixHT.Add(radarCoordinates, generalMatrix);
		}
		return generalMatrix;
	}

	private GeneralMatrix ObtainTranslationMatrix(CoordinatesWGS84 radarCoordinates)
	{
		GeneralMatrix generalMatrix = null;
		if (translationMatrixHT == null)
		{
			translationMatrixHT = new Dictionary<CoordinatesWGS84, GeneralMatrix>(16);
		}
		if (translationMatrixHT.ContainsKey(radarCoordinates))
		{
			generalMatrix = translationMatrixHT[radarCoordinates];
		}
		else
		{
			generalMatrix = CalculateTranslationMatrix(radarCoordinates, A, E2);
			translationMatrixHT.Add(radarCoordinates, generalMatrix);
		}
		return generalMatrix;
	}

	private GeneralMatrix ObtainPositionRadarMatrix(CoordinatesWGS84 radarCoordinates)
	{
		GeneralMatrix generalMatrix = null;
		lock (PositionRadarMatrixLock)
		{
			if (positionRadarMatrixHT == null)
			{
				positionRadarMatrixHT = new Dictionary<CoordinatesWGS84, GeneralMatrix>(16);
			}
			if (positionRadarMatrixHT.ContainsKey(radarCoordinates))
			{
				generalMatrix = positionRadarMatrixHT[radarCoordinates];
			}
			else
			{
				generalMatrix = CalculatePositionRadarMatrix(T1, ObtainTranslationMatrix(radarCoordinates), ObtainRotationMatrix(radarCoordinates));
				positionRadarMatrixHT.Add(radarCoordinates, generalMatrix);
			}
		}
		return generalMatrix;
	}

	private GeneralMatrix ObtainRotationRadarMatrix(CoordinatesWGS84 radarCoordinates)
	{
		GeneralMatrix generalMatrix = null;
		lock (RotationRadarMatrixLock)
		{
			if (rotationRadarMatrixHT == null)
			{
				rotationRadarMatrixHT = new Dictionary<CoordinatesWGS84, GeneralMatrix>(16);
			}
			if (rotationRadarMatrixHT.ContainsKey(radarCoordinates))
			{
				generalMatrix = rotationRadarMatrixHT[radarCoordinates];
			}
			else
			{
				generalMatrix = CalculateRotationRadarMatrix(R1, ObtainRotationMatrix(radarCoordinates));
				rotationRadarMatrixHT.Add(radarCoordinates, generalMatrix);
			}
		}
		return generalMatrix;
	}
}

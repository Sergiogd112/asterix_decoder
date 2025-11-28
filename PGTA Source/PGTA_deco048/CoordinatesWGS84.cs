using System;
using System.Text;

namespace PGTA_deco048;

public class CoordinatesWGS84 : Coordinates
{
	private double lat;

	private double lon;

	private double height;

	public double Height
	{
		get
		{
			return height;
		}
		set
		{
			height = value;
		}
	}

	public double Lat
	{
		get
		{
			return lat;
		}
		set
		{
			lat = value;
		}
	}

	public double Lon
	{
		get
		{
			return lon;
		}
		set
		{
			lon = value;
		}
	}

	public CoordinatesWGS84()
	{
		lat = 0.0;
		lon = 0.0;
		height = 0.0;
	}

	public CoordinatesWGS84(double lat, double lon)
	{
		this.lat = lat;
		this.lon = lon;
		height = 0.0;
	}

	public CoordinatesWGS84(string lat, string lon, double h)
	{
		this.lat = Convert.ToDouble(lat) * (Math.PI / 180.0);
		this.lon = Convert.ToDouble(lon) * (Math.PI / 180.0);
		height = h;
	}

	public CoordinatesWGS84(double lat, double lon, double height)
	{
		this.lat = lat;
		this.lon = lon;
		this.height = height;
	}

	public override string ToString()
	{
		StringBuilder stringBuilder = new StringBuilder();
		GeoUtils.Radians2LatLon(lat, out var d, out var d2, out var d3, out var ns);
		stringBuilder.AppendFormat("{0:d2}:{1:d2}:{2:f4}" + ((ns == 0) ? 'N' : 'S') + " ", (int)d, (int)d2, d3);
		GeoUtils.Radians2LatLon(lon, out d, out d2, out d3, out ns);
		stringBuilder.AppendFormat("{0:d3}:{1:d2}:{2:f4}" + ((ns == 0) ? 'E' : 'W') + " ", (int)d, (int)d2, d3);
		stringBuilder.AppendFormat("{0:f4}m", height);
		stringBuilder.Append(Environment.NewLine);
		stringBuilder.AppendFormat("lat:{0:f9} lon:{1:f9}", Lat * (180.0 / Math.PI), Lon * (180.0 / Math.PI));
		return stringBuilder.ToString();
	}
}

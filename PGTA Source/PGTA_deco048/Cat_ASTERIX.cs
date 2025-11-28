namespace PGTA_deco048;

public class Cat_ASTERIX
{
	private bool IsPuro;

	private bool IsFijo;

	private bool IsOnGround;

	private double lat;

	private double lon;

	public string CAT { get; set; }

	public string SAC { get; set; }

	public string SIC { get; set; }

	public string Time { get; set; }

	public string Latitud { get; set; }

	public string Longitud { get; set; }

	public string h__wgs84 { get; set; }

	public string h__ft { get; set; }

	public string RHO { get; set; }

	public string THETA { get; set; }

	public string Mode__3A { get; set; }

	public string Flight__Level { get; set; }

	public string ModeC__corrected { get; set; }

	public string Target__address { get; set; }

	public string Target__identification { get; set; }

	public string Mode__S { get; set; }

	public string BP { get; set; }

	public string RA { get; set; }

	public string TTA { get; set; }

	public string GS { get; set; }

	public string TAR { get; set; }

	public string TAS { get; set; }

	public string HDG { get; set; }

	public string IAS { get; set; }

	public string MACH { get; set; }

	public string BAR { get; set; }

	public string IVV { get; set; }

	public string Track__number { get; set; }

	public string Ground__Speed_kt { get; set; }

	public string Heading { get; set; }

	public string STAT_230 { get; set; }

	public bool Get_Puro()
	{
		return IsPuro;
	}

	public bool Get_Fijo()
	{
		return IsFijo;
	}

	public bool Get_Ground()
	{
		return IsOnGround;
	}

	public double Get_lat()
	{
		return lat;
	}

	public double Get_lon()
	{
		return lon;
	}

	public Cat_ASTERIX(Cat_048 x)
	{
		CAT = x.CAT;
		SAC = x.SAC;
		SIC = x.SIC;
		Time = x.Time;
		Latitud = x.Latitud;
		Longitud = x.Longitud;
		h__wgs84 = x.h__wgs84;
		h__ft = x.h__ft;
		RHO = x.RHO;
		THETA = x.THETA;
		Mode__3A = x.Mode__3A;
		Flight__Level = x.Flight__Level;
		ModeC__corrected = x.ModeC__corrected;
		Target__address = x.Target__address;
		Target__identification = x.Target__identification;
		Mode__S = x.Mode__S;
		BP = x.BP;
		RA = x.RA;
		TTA = x.TTA;
		GS = x.GS;
		TAR = x.TAR;
		TAS = x.TAS;
		HDG = x.HDG;
		IAS = x.IAS;
		MACH = x.MACH;
		BAR = x.BAR;
		IVV = x.IVV;
		Track__number = x.Track__number;
		Ground__Speed_kt = x.Ground__Speed_kt;
		Heading = x.Heading;
		STAT_230 = x.STAT_230;
		IsPuro = x.Get_Puro();
		IsFijo = x.Get_Fijo();
		IsOnGround = x.Get_Ground();
		lat = x.Get_lat();
		lon = x.Get_lon();
	}

	public Cat_ASTERIX(Cat_021 x)
	{
		CAT = x.CAT;
		SAC = x.SAC;
		SIC = x.SIC;
		Time = x.Time;
		Latitud = x.Latitud;
		Longitud = x.Longitud;
		h__wgs84 = x.h__wgs84;
		h__ft = x.h__ft;
		RHO = "N/A";
		THETA = "N/A";
		Mode__3A = x.Mode__3A;
		Flight__Level = x.Flight__Level;
		ModeC__corrected = x.ModeC__corrected;
		Target__address = x.Target__address;
		Target__identification = x.Target__identification;
		Mode__S = "N/A";
		BP = x.BP;
		RA = x.RA;
		TTA = x.TTA;
		GS = x.GS;
		TAR = x.TAR;
		TAS = x.TAS;
		HDG = x.HDG;
		IAS = x.IAS;
		MACH = "N/A";
		BAR = x.BAR;
		IVV = x.IVV;
		Track__number = "N/A";
		Ground__Speed_kt = x.Ground__Speed_kt;
		Heading = x.Heading;
		STAT_230 = "N/A";
		IsPuro = x.Get_Puro();
		IsFijo = x.Get_Fijo();
		IsOnGround = x.Get_Ground();
		lat = x.Get_lat();
		lon = x.Get_lon();
	}
}

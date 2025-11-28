using System;
using System.Collections.Generic;
using System.Linq;

namespace PGTA_deco048;

public class Cat_021
{
	private bool IsPuro;

	private bool IsFijo;

	private bool IsOnGround;

	private bool corrected;

	private bool TBC;

	private bool filter;

	private double FL;

	private int time_s;

	private double time_decimals;

	private double lat;

	private double lon;

	private List<byte> datablock;

	private int offset;

	public string CAT { get; set; }

	public string SAC { get; set; }

	public string SIC { get; set; }

	public string Time { get; set; }

	public string Latitud { get; set; }

	public string Longitud { get; set; }

	public string h__wgs84 { get; set; }

	public string h__ft { get; set; }

	public string Mode__3A { get; set; }

	public string Flight__Level { get; set; }

	public string ModeC__corrected { get; set; }

	public string Target__address { get; set; }

	public string Target__identification { get; set; }

	public string BP { get; set; }

	public string RA { get; set; }

	public string TTA { get; set; }

	public string GS { get; set; }

	public string TAR { get; set; }

	public string TAS { get; set; }

	public string HDG { get; set; }

	public string IAS { get; set; }

	public string BAR { get; set; }

	public string IVV { get; set; }

	public string Ground__Speed_kt { get; set; }

	public string Heading { get; set; }

	public void Set_corrected(bool x)
	{
		corrected = x;
	}

	public bool Get_TBC()
	{
		return TBC;
	}

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

	public bool Get_filter()
	{
		return filter;
	}

	public double Get_FL_double()
	{
		return FL;
	}

	public double Get_lat()
	{
		return lat;
	}

	public double Get_lon()
	{
		return lon;
	}

	public int Get_timing()
	{
		return time_s;
	}

	public bool Get_corrected()
	{
		return corrected;
	}

	public double Get_timing_dec()
	{
		return time_decimals;
	}

	public Cat_021(double time, double U, double V, double IAS, double Altitude)
	{
		this.IAS = Convert.ToString(IAS);
		ModeC__corrected = Convert.ToString(Altitude);
		time_decimals = time;
		Time = Convert.ToString(TimeSpan.FromSeconds(time).ToString("hh\\:mm\\:ss\\:fff"));
	}

	public Cat_021(List<byte> FSPEC, List<byte> datablock)
	{
		inicio_variables();
		CAT = "CAT021";
		bool flag = false;
		this.datablock = datablock;
		int[] array = decimal2bin(FSPEC[0], 8);
		offset = 0;
		int num = 1;
		if (num == 1)
		{
			if (array[0] == 1)
			{
				Source_Identifier();
			}
			if (array[1] == 1)
			{
				filter = Target_report();
			}
			if (array[2] == 1)
			{
				offset += 2;
			}
			if (array[3] == 1)
			{
				offset++;
			}
			if (array[4] == 1)
			{
				offset += 3;
			}
			if (array[5] == 1)
			{
				offset += 6;
			}
			if (array[6] == 1)
			{
				WSG84_position_HD();
			}
			if (array[7] == 1)
			{
				num = 2;
			}
		}
		if (num == 2 && !filter)
		{
			int[] array2 = decimal2bin(FSPEC[1], 8);
			if (array2[0] == 1)
			{
				offset += 3;
			}
			if (array2[1] == 1)
			{
				offset += 2;
			}
			if (array2[2] == 1)
			{
				offset += 2;
			}
			if (array2[3] == 1)
			{
				target_adress_func();
			}
			if (array2[4] == 1)
			{
				time_function();
			}
			if (array2[5] == 1)
			{
				offset += 4;
			}
			if (array2[6] == 1)
			{
				offset += 3;
			}
			if (array2[7] == 1)
			{
				num = 3;
			}
		}
		if (num == 3 && !filter)
		{
			int[] array3 = decimal2bin(FSPEC[2], 8);
			if (array3[0] == 1)
			{
				offset += 4;
			}
			if (array3[1] == 1)
			{
				offset += 2;
			}
			if (array3[2] == 1)
			{
				offset += variable_item(offset, this.datablock);
			}
			if (array3[3] == 1)
			{
				offset++;
			}
			if (array3[4] == 1)
			{
				mode_3A_function();
			}
			if (array3[5] == 1)
			{
				offset += 2;
			}
			if (array3[6] == 1)
			{
				Flight_level();
			}
			if (array3[7] == 1)
			{
				num = 4;
			}
		}
		if (num == 4 && !filter)
		{
			int[] array4 = decimal2bin(FSPEC[3], 8);
			if (array4[0] == 1)
			{
				offset += 2;
			}
			if (array4[1] == 1)
			{
				offset++;
			}
			if (array4[2] == 1)
			{
				offset += 2;
			}
			if (array4[3] == 1)
			{
				offset += 2;
			}
			if (array4[4] == 1)
			{
				offset += 4;
			}
			if (array4[5] == 1)
			{
				offset += 2;
			}
			if (array4[6] == 1)
			{
				offset += 3;
			}
			if (array4[7] == 1)
			{
				num = 5;
			}
		}
		if (num == 5 && !filter)
		{
			int[] array5 = decimal2bin(FSPEC[4], 8);
			if (array5[0] == 1)
			{
				target_identification();
			}
			if (array5[1] == 1)
			{
				offset++;
			}
			if (array5[2] == 1)
			{
				meteo_fun();
			}
			if (array5[3] == 1)
			{
				offset += 2;
			}
			if (array5[4] == 1)
			{
				offset += 2;
			}
			if (array5[5] == 1)
			{
				trajectory_fun();
			}
			if (array5[6] == 1)
			{
				offset++;
			}
			if (array5[7] == 1)
			{
				num = 6;
			}
		}
		if (num == 6 && !filter)
		{
			int[] array6 = decimal2bin(FSPEC[5], 8);
			if (array6[0] == 1)
			{
				offset++;
			}
			if (array6[1] == 1)
			{
				offset += variable_item(offset, this.datablock);
			}
			if (array6[2] == 1)
			{
				offset++;
			}
			if (array6[3] == 1)
			{
				mode_s_function();
			}
			if (array6[4] == 1)
			{
				offset += 7;
			}
			if (array6[5] == 1)
			{
				offset++;
			}
			if (array6[6] == 1)
			{
				AGES();
			}
			if (array6[7] == 1)
			{
				num = 7;
			}
		}
		if (num == 7 && !filter)
		{
			int[] array7 = decimal2bin(FSPEC[6], 8);
			_ = array7[0];
			_ = 1;
			_ = array7[1];
			_ = 1;
			_ = array7[2];
			_ = 1;
			_ = array7[3];
			_ = 1;
			_ = array7[4];
			_ = 1;
			if (array7[5] == 1)
			{
				RE();
			}
			_ = array7[6];
			_ = 1;
			_ = array7[7];
			_ = 1;
		}
		this.datablock = null;
		if (!(BP != "N/A") || !(Flight__Level != "N/A") || !(BP != "NV") || flag)
		{
			return;
		}
		if (Convert.ToDouble(Flight__Level) <= 60.0)
		{
			double num2 = Convert.ToDouble(BP);
			decimal d = Convert.ToDecimal(FL) * 100m + (Convert.ToDecimal(BP) - Convert.ToDecimal(1013.2)) * 30m;
			if (num2 > 1013.3)
			{
				ModeC__corrected = Convert.ToString(decimal.Round(d, 2));
				corrected = true;
			}
			else if (num2 <= 1013.3)
			{
				TBC = true;
			}
		}
		else
		{
			ModeC__corrected = "";
		}
	}

	public int[] convert(int n, int num)
	{
		int[] array = new int[num];
		int num2 = num - 1;
		while (n > 0)
		{
			array[num2] = n % 2;
			n /= 2;
			num2--;
		}
		return array;
	}

	public int bin2decimal(int[] a)
	{
		double num = 0.0;
		double num2 = 0.0;
		for (int num3 = a.Length; num3 > 0; num3--)
		{
			num += (double)a[num3 - 1] * Math.Pow(2.0, num2);
			num2 += 1.0;
		}
		return Convert.ToInt32(num);
	}

	public int[] decimal2bin(int n, int num)
	{
		int[] array = new int[num];
		int num2 = num - 1;
		while (n > 0)
		{
			array[num2] = n % 2;
			n /= 2;
			num2--;
		}
		return array;
	}

	public int variable_item(int offset, List<byte> datablock)
	{
		int num = 1;
		byte b = datablock[offset];
		while (b % 2 != 0)
		{
			b = datablock[offset + num];
			num++;
		}
		return num;
	}

	public int[] two_complement(int[] a)
	{
		int i;
		for (i = 0; i < a.Length; i++)
		{
			if (a[i] == 0)
			{
				a[i] = 1;
			}
			else
			{
				a[i] = 0;
			}
		}
		while (i > 0)
		{
			if (a[i - 1] == 0)
			{
				a[i - 1] = 1;
				i = -1;
			}
			else
			{
				a[i - 1] = 0;
				i--;
			}
		}
		return a;
	}

	public string bin2hex(string uno, string dos, int num)
	{
		List<string> list = new List<string> { uno, dos };
		List<string> list2 = new List<string>();
		for (int i = 0; i < num; i++)
		{
			switch (list[i])
			{
			case "0000":
				list2.Add("0");
				break;
			case "0001":
				list2.Add("1");
				break;
			case "0010":
				list2.Add("2");
				break;
			case "0011":
				list2.Add("3");
				break;
			case "0100":
				list2.Add("4");
				break;
			case "0101":
				list2.Add("5");
				break;
			case "0110":
				list2.Add("6");
				break;
			case "0111":
				list2.Add("7");
				break;
			case "1000":
				list2.Add("8");
				break;
			case "1001":
				list2.Add("9");
				break;
			case "1010":
				list2.Add("A");
				break;
			case "1011":
				list2.Add("B");
				break;
			case "1100":
				list2.Add("C");
				break;
			case "1101":
				list2.Add("D");
				break;
			case "1110":
				list2.Add("E");
				break;
			case "1111":
				list2.Add("F");
				break;
			}
		}
		return string.Join<string>("", (IEnumerable<string>)list2);
	}

	public string decode_ASCII(string input)
	{
		return input switch
		{
			"000001" => "A", 
			"000010" => "B", 
			"000011" => "C", 
			"000100" => "D", 
			"000101" => "E", 
			"000110" => "F", 
			"000111" => "G", 
			"001000" => "H", 
			"001001" => "I", 
			"001010" => "J", 
			"001011" => "K", 
			"001100" => "L", 
			"001101" => "M", 
			"001110" => "N", 
			"001111" => "O", 
			"010000" => "P", 
			"010001" => "Q", 
			"010010" => "R", 
			"010011" => "S", 
			"010100" => "T", 
			"010101" => "U", 
			"010110" => "V", 
			"010111" => "W", 
			"011000" => "X", 
			"011001" => "Y", 
			"011010" => "Z", 
			"110000" => "0", 
			"110001" => "1", 
			"110010" => "2", 
			"110011" => "3", 
			"110100" => "4", 
			"110101" => "5", 
			"110110" => "6", 
			"110111" => "7", 
			"111000" => "8", 
			"111001" => "9", 
			_ => ",", 
		};
	}

	public void Source_Identifier()
	{
		SAC = Convert.ToString(datablock[offset]);
		SIC = Convert.ToString(datablock[offset + 1]);
		offset += 2;
	}

	public void WSG84_position_HD()
	{
		double num = Convert.ToDouble(40.9);
		double num2 = Convert.ToDouble(41.7);
		double num3 = Convert.ToDouble(1.5);
		double num4 = Convert.ToDouble(2.6);
		byte b = datablock[offset];
		byte b2 = datablock[offset + 1];
		byte b3 = datablock[offset + 2];
		byte b4 = datablock[offset + 3];
		byte b5 = datablock[offset + 4];
		byte b6 = datablock[offset + 5];
		byte num5 = datablock[offset + 6];
		byte b7 = datablock[offset + 7];
		string[] array = new string[2];
		int n = (b << 8) | b2;
		int n2 = (b3 << 8) | b4;
		int n3 = (b5 << 8) | b6;
		int n4 = (num5 << 8) | b7;
		int[] array2 = convert(n, 16).Concat(convert(n2, 16)).ToArray();
		int[] array3 = convert(n3, 16).Concat(convert(n4, 16)).ToArray();
		if (array2[0] == 0)
		{
			array[0] = Convert.ToString(Convert.ToDouble(bin2decimal(array2)) * 180.0 / Math.Pow(2.0, 30.0));
		}
		else
		{
			int[] a = two_complement(array2);
			int num6 = -bin2decimal(a);
			array[0] = Convert.ToString((double)(num6 * 180) / Math.Pow(2.0, 30.0));
		}
		if (array3[0] == 0)
		{
			array[1] = Convert.ToString(Convert.ToDouble(bin2decimal(array3)) * 180.0 / Math.Pow(2.0, 30.0));
		}
		else
		{
			int[] a2 = two_complement(array3);
			int num7 = -bin2decimal(a2);
			array[1] = Convert.ToString((double)(num7 * 180) / Math.Pow(2.0, 30.0));
		}
		lat = Convert.ToDouble(array[0]);
		lon = Convert.ToDouble(array[1]);
		Latitud = array[0];
		Longitud = array[1];
		if (lat < num2 && lat > num)
		{
			if (!(lon < num4) || !(lon > num3))
			{
				filter = true;
			}
		}
		else
		{
			filter = true;
		}
		offset += 8;
	}

	public void target_adress_func()
	{
		byte item = datablock[offset];
		byte item2 = datablock[offset + 1];
		byte item3 = datablock[offset + 2];
		List<byte> list = new List<byte> { item, item2, item3 };
		List<string> list2 = new List<string>();
		for (int i = 0; i < 3; i++)
		{
			int[] array = convert(list[i], 8);
			List<string> values = new List<string>
			{
				Convert.ToString(array[0]),
				Convert.ToString(array[1]),
				Convert.ToString(array[2]),
				Convert.ToString(array[3])
			};
			List<string> values2 = new List<string>
			{
				Convert.ToString(array[4]),
				Convert.ToString(array[5]),
				Convert.ToString(array[6]),
				Convert.ToString(array[7])
			};
			string uno = string.Join<string>("", (IEnumerable<string>)values);
			string dos = string.Join<string>("", (IEnumerable<string>)values2);
			list2.Add(bin2hex(uno, dos, 2));
		}
		Target__address = string.Join<string>("", (IEnumerable<string>)list2);
		offset += 3;
	}

	public void target_identification()
	{
		byte b = datablock[offset];
		byte b2 = datablock[offset + 1];
		byte b3 = datablock[offset + 2];
		byte b4 = datablock[offset + 3];
		byte num = datablock[offset + 4];
		byte b5 = datablock[offset + 5];
		int n = (b << 8) | b2;
		int n2 = (b3 << 8) | b4;
		int n3 = (num << 8) | b5;
		int[] array = convert(n, 16).Concat(convert(n2, 16)).ToArray().Concat(convert(n3, 16))
			.ToArray();
		int num2 = 0;
		int num3 = 0;
		List<string> list = new List<string>();
		while (num2 < 8)
		{
			List<string> values = new List<string>
			{
				Convert.ToString(array[num3]),
				Convert.ToString(array[num3 + 1]),
				Convert.ToString(array[num3 + 2]),
				Convert.ToString(array[num3 + 3]),
				Convert.ToString(array[num3 + 4]),
				Convert.ToString(array[num3 + 5])
			};
			string input = string.Join<string>("", (IEnumerable<string>)values);
			string text = decode_ASCII(input);
			if (text != ",")
			{
				list.Add(text);
			}
			num2++;
			num3 += 6;
		}
		Target__identification = string.Join<string>("", (IEnumerable<string>)list);
		offset += 6;
	}

	public void AGES()
	{
		List<byte> list = new List<byte>();
		byte b = datablock[offset];
		offset++;
		if (b % 2 != 0)
		{
			list.Add(b);
			while (b % 2 != 0)
			{
				b = datablock[offset];
				list.Add(b);
				offset++;
			}
		}
		else
		{
			list.Add(b);
		}
		int i = 0;
		int num = 1;
		for (; i < list.Count; i++)
		{
			byte n = list[i];
			int[] array = convert(n, 8);
			for (int j = 0; j < 7; j++)
			{
				if (array[j] == 1)
				{
					Convert.ToString((double)(int)datablock[offset] * 0.1);
					offset++;
				}
				num++;
			}
		}
	}

	public void mode_3A_function()
	{
		byte num = datablock[offset];
		byte b = datablock[offset + 1];
		int n = (num << 8) | b;
		int[] array = convert(n, 16);
		List<int> list = new List<int>();
		for (int i = 0; i < 12; i += 3)
		{
			int item = bin2decimal(new int[3]
			{
				array[i + 4],
				array[i + 5],
				array[i + 6]
			});
			list.Add(item);
		}
		int num2 = list[0] * 1000 + list[1] * 100 + list[2] * 10 + list[3];
		if (num2 < 1000)
		{
			Mode__3A = "0" + Convert.ToString(num2);
		}
		else
		{
			Mode__3A = Convert.ToString(num2);
		}
		if (Mode__3A == "7777")
		{
			IsFijo = true;
		}
		offset += 2;
	}

	public void time_function()
	{
		byte num = datablock[offset];
		byte b = datablock[offset + 1];
		byte b2 = datablock[offset + 2];
		int num2 = (((num << 8) | b) << 8) | b2;
		Time = TimeSpan.FromSeconds((double)num2 * Math.Pow(2.0, -7.0)).ToString("hh\\:mm\\:ss\\:fff");
		offset += 3;
	}

	public void Flight_level()
	{
		byte num = datablock[offset];
		byte b = datablock[offset + 1];
		int num2 = (num << 8) | b;
		if (num2 < 32768)
		{
			Flight__Level = Convert.ToString((double)num2 * 0.25);
			FL = (double)num2 * 0.25;
		}
		else
		{
			int[] a = two_complement(decimal2bin(num2, 16));
			int num3 = -bin2decimal(a);
			Flight__Level = Convert.ToString((double)num3 * 0.25);
			FL = (double)num3 * 0.25;
		}
		offset += 2;
	}

	public bool Target_report()
	{
		byte n = datablock[offset];
		offset++;
		bool result = false;
		if (convert(n, 8)[7] == 1)
		{
			byte n2 = datablock[offset];
			offset++;
			int[] array = convert(n2, 8);
			result = ((array[1] != 0) ? true : false);
			if (array[7] == 1)
			{
				_ = datablock[offset];
				offset++;
			}
		}
		return result;
	}

	public void mode_s_function()
	{
		byte b = datablock[offset];
		offset++;
		for (int i = 0; i < b; i++)
		{
			offset += 8;
		}
	}

	public void meteo_fun()
	{
		byte n = datablock[offset];
		offset++;
		int[] array = convert(n, 8);
		if (array[0] == 1)
		{
			offset += 2;
		}
		if (array[1] == 1)
		{
			offset += 2;
		}
		if (array[2] == 1)
		{
			offset += 2;
		}
		if (array[3] == 1)
		{
			offset++;
		}
	}

	public void trajectory_fun()
	{
		byte n = datablock[offset];
		offset++;
		int[] array = convert(n, 8);
		if (array[0] == 1)
		{
			offset++;
		}
		if (array[1] == 1)
		{
			byte b = datablock[offset];
			offset++;
			for (int i = 0; i < b; i++)
			{
				offset += 15;
			}
		}
	}

	public void inicio_variables()
	{
		SAC = "N/A";
		SIC = "N/A";
		Time = "N/A";
		Mode__3A = "N/A";
		Flight__Level = "N/A";
		Target__address = "N/A";
		Target__identification = "N/A";
		BP = "N/A";
		RA = "N/A";
		TTA = "N/A";
		GS = "N/A";
		TAR = "N/A";
		TAS = "N/A";
		HDG = "N/A";
		IAS = "N/A";
		BAR = "N/A";
		IVV = "N/A";
		Ground__Speed_kt = "N/A";
		Heading = "N/A";
		Latitud = "N/A";
		Longitud = "N/A";
		h__wgs84 = "N/A";
		h__ft = "N/A";
	}

	public void RE()
	{
		byte n = datablock[offset + 1];
		offset += 2;
		int[] array = convert(n, 8);
		if (array[0] == 1)
		{
			byte num = datablock[offset];
			byte b = datablock[offset + 1];
			offset += 2;
			int n2 = (num << 8) | b;
			int[] array2 = convert(n2, 16);
			int[] array3 = new int[12];
			for (int i = 0; i < 12; i++)
			{
				array3[i] = array2[i + 4];
			}
			BP = Convert.ToString((double)bin2decimal(array3) * 0.1 + 800.0);
		}
		if (array[1] == 1)
		{
			offset += 2;
		}
		if (array[2] == 1)
		{
			offset++;
		}
		if (array[3] == 1)
		{
			offset++;
		}
	}
}

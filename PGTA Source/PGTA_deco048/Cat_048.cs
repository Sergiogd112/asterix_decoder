using System;
using System.Collections.Generic;
using System.Linq;

namespace PGTA_deco048;

public class Cat_048
{
	private bool IsPuro;

	private bool IsFijo;

	private bool IsOnGround;

	private bool corrected;

	private bool TBC;

	private bool filter;

	private double rho_m;

	private double theta_rad;

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

	public string TYP_020 { get; set; }

	public string SIM_020 { get; set; }

	public string RDP_020 { get; set; }

	public string SPI_020 { get; set; }

	public string RAB_020 { get; set; }

	public string TST_020 { get; set; }

	public string ERR_020 { get; set; }

	public string XPP_020 { get; set; }

	public string ME_020 { get; set; }

	public string MI_020 { get; set; }

	public string FOE_FRI_020 { get; set; }

	public string RHO { get; set; }

	public string THETA { get; set; }

	public string V_070 { get; set; }

	public string G_070 { get; set; }

	public string Mode__3A { get; set; }

	public string V_090 { get; set; }

	public string G_090 { get; set; }

	public string Flight__Level { get; set; }

	public string ModeC__corrected { get; set; }

	public string SRL_130 { get; set; }

	public string SRR_130 { get; set; }

	public string SAM_130 { get; set; }

	public string PRL_130 { get; set; }

	public string PAM_130 { get; set; }

	public string RPD_130 { get; set; }

	public string APD_130 { get; set; }

	public string Target__address { get; set; }

	public string Target__identification { get; set; }

	public string Mode__S { get; set; }

	public string MCP_STATUS { get; set; }

	public string MCP__ALT { get; set; }

	public string FMS_STATUS { get; set; }

	public string FMS__ALT { get; set; }

	public string BP_STATUS { get; set; }

	public string BP { get; set; }

	public string MODE__STATUS { get; set; }

	public string VNAV { get; set; }

	public string ALT_HOLD { get; set; }

	public string APP { get; set; }

	public string TARGET_ALT_STATUS { get; set; }

	public string TARGET_ALT_SOURCE { get; set; }

	public string RA_STATUS { get; set; }

	public string RA { get; set; }

	public string TTA_STATUS { get; set; }

	public string TTA { get; set; }

	public string GS_STATUS { get; set; }

	public string GS { get; set; }

	public string TAR_STATUS { get; set; }

	public string TAR { get; set; }

	public string TAS_STATUS { get; set; }

	public string TAS { get; set; }

	public string HDG_STATUS { get; set; }

	public string HDG { get; set; }

	public string IAS_STATUS { get; set; }

	public string IAS { get; set; }

	public string MACH_STATUS { get; set; }

	public string MACH { get; set; }

	public string BAR_STATUS { get; set; }

	public string BAR { get; set; }

	public string IVV_STATUS { get; set; }

	public string IVV { get; set; }

	public string Track__number { get; set; }

	public string X__Component { get; set; }

	public string Y__Component { get; set; }

	public string Ground__Speed_kt { get; set; }

	public string Heading { get; set; }

	public string CNF_170 { get; set; }

	public string RAD_170 { get; set; }

	public string DOU_170 { get; set; }

	public string MAH_170 { get; set; }

	public string CDM_170 { get; set; }

	public string TRE_170 { get; set; }

	public string GHO_170 { get; set; }

	public string SUP_170 { get; set; }

	public string TCC_170 { get; set; }

	public string Measured__Height { get; set; }

	public string COM_230 { get; set; }

	public string STAT_230 { get; set; }

	public string SI_230 { get; set; }

	public string MSCC_230 { get; set; }

	public string ARC_230 { get; set; }

	public string AIC_230 { get; set; }

	public string B1A_230 { get; set; }

	public string B1B_230 { get; set; }

	public bool Get_Filter()
	{
		return filter;
	}

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

	public Cat_048(double time, double U, double V, double IAS, double Altitude)
	{
		this.IAS = Convert.ToString(IAS);
		ModeC__corrected = Convert.ToString(Altitude);
		time_decimals = time;
		Time = Convert.ToString(TimeSpan.FromSeconds(time).ToString("hh\\:mm\\:ss\\:fff"));
	}

	public Cat_048(List<byte> FSPEC, List<byte> datablock)
	{
		inicio_variables();
		CAT = "CAT048";
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
				t_function();
			}
			if (array[2] == 1)
			{
				target_report();
			}
			if (array[3] == 1)
			{
				pos_polar();
			}
			if (array[4] == 1)
			{
				mode_3A_function();
			}
			if (array[5] == 1)
			{
				FL_function();
			}
			if (array[6] == 1)
			{
				radar_plot();
			}
			if (array[7] == 1)
			{
				num = 2;
			}
		}
		if (num == 2)
		{
			int[] array2 = decimal2bin(FSPEC[1], 8);
			if (array2[0] == 1)
			{
				target_adress_func();
			}
			if (array2[1] == 1)
			{
				target_identification();
			}
			if (array2[2] == 1)
			{
				mode_s_function();
			}
			if (array2[3] == 1)
			{
				track_number();
			}
			if (array2[4] == 1)
			{
				pos_cartesian();
			}
			if (array2[5] == 1)
			{
				velocity_polar();
			}
			if (array2[6] == 1)
			{
				track_status();
			}
			if (array2[7] == 1)
			{
				num = 3;
			}
		}
		if (num == 3)
		{
			int[] array3 = decimal2bin(FSPEC[2], 8);
			if (array3[0] == 1)
			{
				offset += 4;
			}
			if (array3[1] == 1)
			{
				offset += variable_item(offset, this.datablock);
			}
			if (array3[2] == 1)
			{
				offset += 2;
			}
			if (array3[3] == 1)
			{
				offset += 4;
			}
			if (array3[4] == 1)
			{
				Measured_height();
			}
			_ = array3[5];
			_ = 1;
			if (array3[6] == 1)
			{
				ACAS();
			}
			if (array3[7] == 1)
			{
				num = 4;
			}
		}
		if (num == 4)
		{
			int[] array4 = decimal2bin(FSPEC[3], 8);
			if (array4[0] == 1)
			{
				offset += 7;
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
				offset++;
			}
			if (array4[4] == 1)
			{
				offset += 2;
			}
			_ = array4[5];
			_ = 1;
			if (array4[6] == 1)
			{
				byte b = datablock[offset];
				offset += b;
			}
			_ = array4[7];
			_ = 1;
		}
		this.datablock = null;
		if (RHO != "N/A" && THETA != "N/A")
		{
			double num2 = Convert.ToDouble(40.9);
			double num3 = Convert.ToDouble(41.7);
			double num4 = Convert.ToDouble(1.5);
			double num5 = Convert.ToDouble(2.6);
			transf_coord();
			if (lat < num3 && lat > num2)
			{
				if (!(lon < num5) || !(lon > num4))
				{
					filter = true;
				}
			}
			else
			{
				filter = true;
			}
		}
		if (Flight__Level == "N/A")
		{
			IsOnGround = true;
		}
		if (!(BP != "N/A") || !(Flight__Level != "N/A") || !(BP != "NV"))
		{
			return;
		}
		if (Convert.ToDouble(Flight__Level) <= 60.0)
		{
			double num6 = Convert.ToDouble(BP);
			decimal d = Convert.ToDecimal(FL) * 100m + (Convert.ToDecimal(BP) - Convert.ToDecimal(1013.2)) * 30m;
			if (num6 > 1013.3)
			{
				ModeC__corrected = Convert.ToString(decimal.Round(d, 2));
				corrected = true;
			}
			else if (num6 <= 1013.3)
			{
				TBC = true;
			}
		}
		else
		{
			ModeC__corrected = "";
		}
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

	public void target_report()
	{
		byte n = datablock[offset];
		offset++;
		int[] array = decimal2bin(n, 8);
		if (array[0] == 0)
		{
			if (array[1] == 0)
			{
				if (array[2] == 0)
				{
					TYP_020 = "No detection";
					IsPuro = true;
				}
				else
				{
					TYP_020 = "PSR";
					IsPuro = true;
				}
			}
			else if (array[2] == 0)
			{
				TYP_020 = "SSR";
				IsPuro = true;
			}
			else
			{
				TYP_020 = "SSR+PSR";
				IsPuro = true;
			}
		}
		else if (array[1] == 0)
		{
			if (array[2] == 0)
			{
				TYP_020 = "Mode S all call";
			}
			else
			{
				TYP_020 = "Mode S roll call";
			}
		}
		else if (array[2] == 0)
		{
			TYP_020 = "Mode S all call + PSR";
		}
		else
		{
			TYP_020 = "Mode S roll call + PSR";
		}
		if (array[3] == 0)
		{
			SIM_020 = "Actual target report";
		}
		else
		{
			SIM_020 = "Simulated target report";
		}
		if (array[4] == 0)
		{
			RDP_020 = "RDP chain 1";
		}
		else
		{
			RDP_020 = "RDP chain 2";
		}
		if (array[5] == 0)
		{
			SPI_020 = "Absence of SPI";
		}
		else
		{
			SPI_020 = "SPI";
		}
		if (array[6] == 0)
		{
			RAB_020 = "Report from Aircraft";
		}
		else
		{
			RAB_020 = "Fixed transponder";
		}
		if (array[7] != 1)
		{
			return;
		}
		byte n2 = datablock[offset];
		offset++;
		int[] array2 = decimal2bin(n2, 8);
		if (array2[0] == 0)
		{
			TST_020 = "Real target";
		}
		else
		{
			TST_020 = "Test target";
		}
		if (array2[1] == 0)
		{
			ERR_020 = "No extended range";
		}
		else
		{
			ERR_020 = "Extended range";
		}
		if (array2[2] == 0)
		{
			XPP_020 = "No X-Pulse";
		}
		else
		{
			XPP_020 = "X-Pulse";
		}
		if (array2[3] == 0)
		{
			ME_020 = "No militar emergency";
		}
		else
		{
			ME_020 = "Militar emergency";
		}
		if (array2[4] == 0)
		{
			MI_020 = "No military ident.";
		}
		else
		{
			MI_020 = "Military ident.";
		}
		if (array2[5] == 0)
		{
			if (array2[6] == 0)
			{
				FOE_FRI_020 = "No Mode 4 interrogation";
			}
			else
			{
				FOE_FRI_020 = "Friend";
			}
		}
		else if (array2[6] == 0)
		{
			FOE_FRI_020 = "Unknown";
		}
		else
		{
			FOE_FRI_020 = "No reply";
		}
	}

	public void pos_polar()
	{
		byte b = datablock[offset];
		byte b2 = datablock[offset + 1];
		byte num = datablock[offset + 2];
		byte b3 = datablock[offset + 3];
		int num2 = (b << 8) | b2;
		int num3 = (num << 8) | b3;
		rho_m = Convert.ToDouble((double)num2 * (1.0 / 256.0) * 1852.0);
		theta_rad = Convert.ToDouble(Convert.ToDecimal((double)num3 * (360.0 / Math.Pow(2.0, 16.0)) * (Math.PI / 180.0)));
		RHO = Convert.ToString(Convert.ToDouble(decimal.Round(Convert.ToDecimal((double)num2 * (1.0 / 256.0)), 6)));
		THETA = Convert.ToString(Convert.ToDouble(decimal.Round(Convert.ToDecimal((double)num3 * (360.0 / Math.Pow(2.0, 16.0))), 6)));
		offset += 4;
	}

	public void pos_cartesian()
	{
		byte b = datablock[offset];
		byte b2 = datablock[offset + 1];
		byte num = datablock[offset + 2];
		byte b3 = datablock[offset + 3];
		int num2 = (b << 8) | b2;
		int num3 = (num << 8) | b3;
		if (num2 >= 32768)
		{
			int[] a = decimal2bin(num2, 16);
			int[] a2 = two_complement(a);
			X__Component = Convert.ToString(Convert.ToDouble((double)(-bin2decimal(a2)) * 1.0 / 128.0));
		}
		else
		{
			X__Component = Convert.ToString(Convert.ToDouble((double)num2 * 1.0 / 128.0));
		}
		if (num3 >= 32768)
		{
			int[] a3 = decimal2bin(num3, 16);
			int[] a4 = two_complement(a3);
			Y__Component = Convert.ToString(Convert.ToDouble((double)(-bin2decimal(a4)) * 1.0 / 128.0));
		}
		else
		{
			Y__Component = Convert.ToString(Convert.ToDouble((double)num3 * 1.0 / 128.0));
		}
		offset += 4;
	}

	public void mode_3A_function()
	{
		byte num = datablock[offset];
		byte b = datablock[offset + 1];
		int n = (num << 8) | b;
		int[] array = decimal2bin(n, 16);
		if (array[0] == 1)
		{
			V_070 = "NV";
		}
		else
		{
			V_070 = "V";
		}
		if (array[1] == 1)
		{
			G_070 = "Garbled";
		}
		else
		{
			G_070 = "Default";
		}
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
		if (num2 < 10)
		{
			Mode__3A = "000" + Convert.ToString(num2);
		}
		else if (num2 < 100)
		{
			Mode__3A = "00" + Convert.ToString(num2);
		}
		else if (num2 < 1000)
		{
			Mode__3A = "0" + Convert.ToString(num2);
		}
		else
		{
			Mode__3A = Convert.ToString(num2);
		}
		offset += 2;
		if (Mode__3A == "7777")
		{
			IsFijo = true;
		}
	}

	public void FL_function()
	{
		byte num = datablock[offset];
		byte b = datablock[offset + 1];
		int n = (num << 8) | b;
		int[] array = decimal2bin(n, 16);
		if (array[0] == 1)
		{
			V_090 = "NV";
		}
		else
		{
			V_090 = "V";
		}
		if (array[1] == 1)
		{
			G_090 = "Garbled";
		}
		else
		{
			G_090 = "Default";
		}
		int i = 0;
		int[] array2 = new int[14];
		for (; i < 14; i++)
		{
			array2[i] = array[i + 2];
		}
		if (array2[0] == 0)
		{
			int num2 = bin2decimal(array2);
			Flight__Level = Convert.ToString((double)num2 * 0.25);
			FL = (double)num2 * 0.25;
		}
		else
		{
			int[] a = two_complement(array2);
			int num3 = -bin2decimal(a);
			Flight__Level = Convert.ToString((double)num3 * 0.25);
			FL = (double)num3 * 0.25;
		}
		offset += 2;
	}

	public void Measured_height()
	{
		byte b = datablock[offset];
		byte b2 = datablock[offset + 1];
		Measured__Height = Convert.ToString(((b << 8) | b2) * 25);
		offset += 2;
	}

	public void radar_plot()
	{
		byte n = datablock[offset];
		offset++;
		int[] array = decimal2bin(n, 8);
		if (array[0] == 1)
		{
			byte b = datablock[offset];
			SRL_130 = Convert.ToString((double)(int)b * 0.044) + " dg";
			offset++;
		}
		if (array[1] == 1)
		{
			byte b2 = datablock[offset];
			SRR_130 = Convert.ToString(b2);
			offset++;
		}
		if (array[2] == 1)
		{
			byte b3 = datablock[offset];
			if (b3 >= 128)
			{
				int[] a = decimal2bin(b3, 8);
				int[] a2 = two_complement(a);
				SAM_130 = Convert.ToString(-bin2decimal(a2)) + " dBm";
			}
			else
			{
				SAM_130 = Convert.ToString(b3) + " dBm";
			}
			offset++;
		}
		if (array[3] == 1)
		{
			byte b4 = datablock[offset];
			PRL_130 = Convert.ToString((double)(int)b4 * 0.044) + " dg";
			offset++;
		}
		if (array[4] == 1)
		{
			byte b5 = datablock[offset];
			if (b5 >= 128)
			{
				int[] a3 = decimal2bin(b5, 8);
				int[] a4 = two_complement(a3);
				PAM_130 = Convert.ToString(-bin2decimal(a4)) + " dBm";
			}
			else
			{
				PAM_130 = Convert.ToString(b5) + " dBm";
			}
			offset++;
		}
		if (array[5] == 1)
		{
			byte b6 = datablock[offset];
			if (b6 >= 128)
			{
				int[] a5 = decimal2bin(b6, 8);
				int[] a6 = two_complement(a5);
				RPD_130 = Convert.ToString(decimal.Round(Convert.ToDecimal((double)(-bin2decimal(a6)) * 1.0 / 256.0), 3)) + " NM";
			}
			else
			{
				RPD_130 = Convert.ToString(decimal.Round(Convert.ToDecimal((double)(int)b6 * 1.0 / 256.0), 3)) + " NM";
			}
			offset++;
		}
		if (array[6] == 1)
		{
			byte b7 = datablock[offset];
			if (b7 >= 128)
			{
				int[] a7 = decimal2bin(b7, 8);
				int[] a8 = two_complement(a7);
				APD_130 = Convert.ToString(decimal.Round(Convert.ToDecimal((double)(-bin2decimal(a8)) * 0.02197265625), 3)) + " dg";
			}
			else
			{
				APD_130 = Convert.ToString(decimal.Round(Convert.ToDecimal((double)(int)b7 * 0.02197265625), 3)) + " dg";
			}
			offset++;
		}
	}

	public void t_function()
	{
		byte num = datablock[offset];
		byte b = datablock[offset + 1];
		byte b2 = datablock[offset + 2];
		double value = (double)((((num << 8) | b) << 8) | b2) * Math.Pow(2.0, -7.0);
		time_s = Convert.ToInt32(value);
		time_decimals = Math.Round(value, 4);
		Time = Convert.ToString(TimeSpan.FromSeconds(value).ToString("hh\\:mm\\:ss\\:fff"));
		offset += 3;
	}

	public void track_number()
	{
		byte b = datablock[offset];
		byte b2 = datablock[offset + 1];
		Track__number = Convert.ToString((b << 8) | b2);
		offset += 2;
	}

	public void track_status()
	{
		byte n = datablock[offset];
		offset++;
		int[] array = decimal2bin(n, 8);
		if (array[0] == 1)
		{
			CNF_170 = "Tentative track";
		}
		else
		{
			CNF_170 = "Confirmed track";
		}
		if (array[1] == 1)
		{
			if (array[2] == 1)
			{
				RAD_170 = "Invalid";
			}
			else
			{
				RAD_170 = "SSR/MODE S";
			}
		}
		else if (array[2] == 1)
		{
			RAD_170 = "PSR";
		}
		else
		{
			RAD_170 = "Combined";
		}
		if (array[3] == 1)
		{
			DOU_170 = "Low confidence";
		}
		else
		{
			DOU_170 = "Normal confidence";
		}
		if (array[4] == 1)
		{
			MAH_170 = "Horitzontal man.sensed";
		}
		else
		{
			MAH_170 = "No horitzontal man.sensed";
		}
		if (array[5] == 1)
		{
			if (array[6] == 1)
			{
				CDM_170 = "Unknown";
			}
			else
			{
				CDM_170 = "Descending";
			}
		}
		else if (array[6] == 1)
		{
			CDM_170 = "Climbing";
		}
		else
		{
			CDM_170 = "Maintaining";
		}
		if (array[7] == 1)
		{
			byte n2 = datablock[offset];
			offset++;
			int[] array2 = decimal2bin(n2, 8);
			if (array2[0] == 1)
			{
				TRE_170 = "Last report";
			}
			else
			{
				TRE_170 = "Track alive";
			}
			if (array2[1] == 1)
			{
				GHO_170 = "Ghost target";
			}
			else
			{
				GHO_170 = "True target";
			}
			if (array2[2] == 1)
			{
				SUP_170 = "YES";
			}
			else
			{
				SUP_170 = "NO";
			}
			if (array2[3] == 1)
			{
				TCC_170 = "Tracking in Radar Plane";
			}
			else
			{
				TCC_170 = "Slat range correction";
			}
		}
	}

	public void velocity_polar()
	{
		byte b = datablock[offset];
		byte b2 = datablock[offset + 1];
		byte num = datablock[offset + 2];
		byte b3 = datablock[offset + 3];
		int num2 = (b << 8) | b2;
		int num3 = (num << 8) | b3;
		Ground__Speed_kt = Convert.ToString(Convert.ToDouble(decimal.Round(Convert.ToDecimal((double)num2 * 0.22), 4)));
		Heading = Convert.ToString(Convert.ToDouble(decimal.Round(Convert.ToDecimal((double)num3 * (360.0 / Math.Pow(2.0, 16.0))), 4)));
		offset += 4;
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
			int[] array = decimal2bin(list[i], 8);
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

	public void ACAS()
	{
		byte n = datablock[offset];
		offset++;
		int[] array = decimal2bin(n, 8);
		if (array[0] == 0)
		{
			if (array[1] == 0)
			{
				if (array[2] == 0)
				{
					COM_230 = "No communication capability";
				}
				else
				{
					COM_230 = "COMM.A and COMM.B capability";
				}
			}
			else if (array[2] == 0)
			{
				COM_230 = "COMM.A and COMM.B capability and Uplink ELM";
			}
			else
			{
				COM_230 = "COMM.A and COMM.B capability and Uplink and downlink ELM";
			}
		}
		else if (array[1] == 0)
		{
			if (array[2] == 0)
			{
				COM_230 = "Level 5 transponder capability";
			}
			else
			{
				COM_230 = "Not assigned";
			}
		}
		else if (array[2] == 0)
		{
			COM_230 = "Not assigned";
		}
		else
		{
			COM_230 = "Not assigned";
		}
		if (array[3] == 0)
		{
			if (array[4] == 0)
			{
				if (array[5] == 0)
				{
					STAT_230 = "No alert, no SPI, aircraft airbone";
				}
				else
				{
					STAT_230 = "No alert, no SPI, aircraft on ground";
					IsOnGround = true;
				}
			}
			else if (array[5] == 0)
			{
				STAT_230 = "Alert, no SPI, aircraft airbone";
			}
			else
			{
				STAT_230 = "Alert, no SPI, aircraft on ground";
				IsOnGround = true;
			}
		}
		else if (array[4] == 0)
		{
			if (array[5] == 0)
			{
				STAT_230 = "Alert, SPI aircraft airbone or on ground";
			}
			else
			{
				STAT_230 = "NO Alert, SPI aircraft airbone or on ground";
			}
		}
		else if (array[5] == 0)
		{
			STAT_230 = "Not assigned";
			IsOnGround = true;
		}
		else
		{
			STAT_230 = "Unknown";
			IsOnGround = true;
		}
		if (array[6] == 0)
		{
			SI_230 = "SI-Code Capable";
		}
		else
		{
			SI_230 = "II-Code Capable";
		}
		byte n2 = datablock[offset];
		offset++;
		int[] array2 = decimal2bin(n2, 8);
		if (array2[0] == 0)
		{
			MSCC_230 = "NO";
		}
		else
		{
			MSCC_230 = "YES";
		}
		if (array2[1] == 0)
		{
			ARC_230 = "100 ft resolution";
		}
		else
		{
			ARC_230 = "25 ft resolution";
		}
		if (array2[2] == 0)
		{
			AIC_230 = "NO";
		}
		else
		{
			AIC_230 = "YES";
		}
		if (array2[3] == 0)
		{
			B1A_230 = "BDS 1,0 bit16=0";
		}
		else
		{
			B1A_230 = "BDS 1,0 bit16=1";
		}
		if (array2[4] == 0)
		{
			if (array2[5] == 0)
			{
				if (array2[6] == 0)
				{
					if (array2[7] == 0)
					{
						B1B_230 = "BDS 1,0 bits 37/40=0000";
					}
					else
					{
						B1B_230 = "BDS 1,0 bits 37/40=0001";
					}
				}
				else if (array2[7] == 0)
				{
					B1B_230 = "BDS 1,0 bits 37/40=0010";
				}
				else
				{
					B1B_230 = "BDS 1,0 bits 37/40=0011";
				}
			}
			else if (array2[6] == 0)
			{
				if (array2[7] == 0)
				{
					B1B_230 = "BDS 1,0 bits 37/40=0100";
				}
				else
				{
					B1B_230 = "BDS 1,0 bits 37/40=0101";
				}
			}
			else if (array2[7] == 0)
			{
				B1B_230 = "BDS 1,0 bits 37/40=0110";
			}
			else
			{
				B1B_230 = "BDS 1,0 bits 37/40=0111";
			}
		}
		else if (array2[5] == 0)
		{
			if (array2[6] == 0)
			{
				if (array2[7] == 0)
				{
					B1B_230 = "BDS 1,0 bits 37/40=1000";
				}
				else
				{
					B1B_230 = "BDS 1,0 bits 37/40=1001";
				}
			}
			else if (array2[7] == 0)
			{
				B1B_230 = "BDS 1,0 bits 37/40=1010";
			}
			else
			{
				B1B_230 = "BDS 1,0 bits 37/40=1011";
			}
		}
		else if (array2[6] == 0)
		{
			if (array2[7] == 0)
			{
				B1B_230 = "BDS 1,0 bits 37/40=1100";
			}
			else
			{
				B1B_230 = "BDS 1,0 bits 37/40=1101";
			}
		}
		else if (array2[7] == 0)
		{
			B1B_230 = "BDS 1,0 bits 37/40=1110";
		}
		else
		{
			B1B_230 = "BDS 1,0 bits 37/40=1111";
		}
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
		int[] array = decimal2bin(n, 16).Concat(decimal2bin(n2, 16)).ToArray().Concat(decimal2bin(n3, 16))
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

	public void mode_s_function()
	{
		List<string> list = new List<string>();
		byte b = datablock[offset];
		offset++;
		for (int i = 0; i < b; i++)
		{
			byte b2 = datablock[offset];
			byte b3 = datablock[offset + 1];
			byte b4 = datablock[offset + 2];
			byte b5 = datablock[offset + 3];
			byte num = datablock[offset + 4];
			byte b6 = datablock[offset + 5];
			byte b7 = datablock[offset + 6];
			int n = (b2 << 8) | b3;
			int n2 = (b4 << 8) | b5;
			int n3 = (((num << 8) | b6) << 8) | b7;
			int[] bits = decimal2bin(n, 16).Concat(decimal2bin(n2, 16)).ToArray().Concat(decimal2bin(n3, 24))
				.ToArray();
			byte n4 = datablock[offset + 7];
			int[] array = decimal2bin(n4, 8);
			List<string> list2 = new List<string>();
			List<string> list3 = new List<string>();
			for (int j = 0; j < 4; j++)
			{
				list2.Add(Convert.ToString(array[j]));
				list3.Add(Convert.ToString(array[j + 4]));
			}
			string uno = string.Join<string>("", (IEnumerable<string>)list2);
			string uno2 = string.Join<string>("", (IEnumerable<string>)list3);
			list.Add(bin2hex(uno, "", 1));
			list.Add(bin2hex(uno2, "", 1));
			offset += 8;
			if (list[list.Count - 2] == "4" && list[list.Count - 1] == "0")
			{
				BDS40(bits);
			}
			else if (list[list.Count - 2] == "5" && list[list.Count - 1] == "0")
			{
				BDS50(bits);
			}
			else if (list[list.Count - 2] == "6" && list[list.Count - 1] == "0")
			{
				BDS60(bits);
			}
		}
		int k = 0;
		Mode__S = "";
		for (; k < list.Count; k += 2)
		{
			if (k == list.Count - 2)
			{
				Mode__S = Mode__S + "BDS:" + list[k] + "," + list[k + 1];
			}
			else
			{
				Mode__S = Mode__S + "BDS:" + list[k] + "," + list[k + 1] + "\n";
			}
		}
	}

	public void BDS40(int[] bits)
	{
		MCP_STATUS = Convert.ToString(bits[0]);
		FMS_STATUS = Convert.ToString(bits[13]);
		BP_STATUS = Convert.ToString(bits[26]);
		MODE__STATUS = Convert.ToString(bits[47]);
		VNAV = Convert.ToString(bits[48]);
		ALT_HOLD = Convert.ToString(bits[49]);
		APP = Convert.ToString(bits[50]);
		TARGET_ALT_STATUS = Convert.ToString(bits[53]);
		if (bits[54] == 0 && bits[55] == 0)
		{
			TARGET_ALT_SOURCE = "0";
		}
		else if (bits[54] == 0 && bits[55] == 1)
		{
			TARGET_ALT_SOURCE = "1";
		}
		else if (bits[54] == 1 && bits[55] == 0)
		{
			TARGET_ALT_SOURCE = "2";
		}
		else if (bits[54] == 1 && bits[55] == 1)
		{
			TARGET_ALT_SOURCE = "3";
		}
		int[] array = new int[12];
		int[] array2 = new int[12];
		int[] array3 = new int[12];
		for (int i = 1; i < 13; i++)
		{
			array[i - 1] = bits[i];
			array2[i - 1] = bits[i + 13];
			array3[i - 1] = bits[i + 26];
		}
		if (MCP_STATUS == "0")
		{
			BP = "NV";
		}
		else
		{
			MCP__ALT = Convert.ToString(bin2decimal(array) * 16);
		}
		if (FMS_STATUS == "0")
		{
			BP = "NV";
		}
		else
		{
			FMS__ALT = Convert.ToString(bin2decimal(array2) * 16);
		}
		if (BP_STATUS == "0")
		{
			BP = "NV";
		}
		else
		{
			BP = Convert.ToString((double)bin2decimal(array3) * 0.1 + 800.0);
		}
	}

	public void BDS50(int[] bits)
	{
		RA_STATUS = Convert.ToString(bits[0]);
		TTA_STATUS = Convert.ToString(bits[11]);
		GS_STATUS = Convert.ToString(bits[23]);
		TAR_STATUS = Convert.ToString(bits[34]);
		TAS_STATUS = Convert.ToString(bits[45]);
		int[] array = new int[9];
		int[] array2 = new int[10];
		int[] array3 = new int[10];
		int[] array4 = new int[9];
		int[] array5 = new int[10];
		for (int i = 1; i < 11; i++)
		{
			array2[i - 1] = bits[i + 12];
			array3[i - 1] = bits[i + 23];
			array5[i - 1] = bits[i + 45];
		}
		for (int j = 1; j < 10; j++)
		{
			array[j - 1] = bits[j + 1];
			array4[j - 1] = bits[j + 35];
		}
		if (RA_STATUS != "0")
		{
			if (bits[1] == 0)
			{
				RA = Convert.ToString(decimal.Round(Convert.ToDecimal((double)bin2decimal(array) * 45.0 / 256.0), 3));
			}
			else
			{
				int[] a = two_complement(array);
				RA = Convert.ToString(decimal.Round(Convert.ToDecimal((double)(-bin2decimal(a)) * 45.0 / 256.0), 3));
			}
		}
		else
		{
			RA = "NV";
		}
		if (TTA_STATUS != "0")
		{
			if (bits[12] == 0)
			{
				TTA = Convert.ToString(decimal.Round(Convert.ToDecimal((double)bin2decimal(array2) * 90.0 / 512.0), 3));
			}
			else
			{
				int[] a2 = two_complement(array2);
				TTA = Convert.ToString(decimal.Round(Convert.ToDecimal((double)(-bin2decimal(a2)) * 90.0 / 512.0), 3));
			}
		}
		else
		{
			TTA = "NV";
		}
		if (GS_STATUS != "0")
		{
			GS = Convert.ToString((double)bin2decimal(array3) * 1024.0 / 512.0);
		}
		else
		{
			GS = "NV";
		}
		if (TAR_STATUS != "0")
		{
			if (bits[35] == 0)
			{
				TAR = Convert.ToString(decimal.Round(Convert.ToDecimal((double)bin2decimal(array4) * 8.0 / 256.0), 3));
			}
			else
			{
				int[] a3 = two_complement(array4);
				TAR = Convert.ToString(decimal.Round(Convert.ToDecimal((double)(-bin2decimal(a3)) * 8.0 / 256.0), 3));
			}
		}
		else
		{
			TAR = "NV";
		}
		if (TAS_STATUS != "0")
		{
			TAS = Convert.ToString(bin2decimal(array5) * 2);
		}
		else
		{
			TAS = "NV";
		}
	}

	public void BDS60(int[] bits)
	{
		HDG_STATUS = Convert.ToString(bits[0]);
		IAS_STATUS = Convert.ToString(bits[12]);
		MACH_STATUS = Convert.ToString(bits[23]);
		BAR_STATUS = Convert.ToString(bits[34]);
		IVV_STATUS = Convert.ToString(bits[45]);
		int[] array = new int[10];
		int[] array2 = new int[10];
		int[] array3 = new int[10];
		int[] array4 = new int[9];
		int[] array5 = new int[9];
		for (int i = 1; i < 11; i++)
		{
			array[i - 1] = bits[i + 1];
			array2[i - 1] = bits[i + 12];
			array3[i - 1] = bits[i + 23];
		}
		for (int j = 1; j < 10; j++)
		{
			array5[j - 1] = bits[j + 46];
			array4[j - 1] = bits[j + 35];
		}
		if (HDG_STATUS != "0")
		{
			if (bits[1] == 0)
			{
				HDG = Convert.ToString(decimal.Round(Convert.ToDecimal((double)bin2decimal(array) * 90.0 / 512.0), 6));
			}
			else
			{
				int[] a = two_complement(array);
				HDG = Convert.ToString(decimal.Round(Convert.ToDecimal((double)(-bin2decimal(a)) * 90.0 / 512.0), 6));
			}
		}
		else
		{
			HDG = "NV";
		}
		if (IAS_STATUS != "0")
		{
			IAS = Convert.ToString(bin2decimal(array2));
		}
		else
		{
			IAS = "NV";
		}
		if (MACH_STATUS != "0")
		{
			MACH = Convert.ToString((double)bin2decimal(array3) * 2.048 / 512.0);
		}
		else
		{
			MACH = "NV";
		}
		if (BAR_STATUS != "0")
		{
			if (bits[35] == 0)
			{
				BAR = Convert.ToString(bin2decimal(array4) * 32);
			}
			else
			{
				int[] a2 = two_complement(array4);
				BAR = Convert.ToString(-bin2decimal(a2) * 32);
			}
		}
		else
		{
			BAR = "NV";
		}
		if (IVV_STATUS != "0")
		{
			if (bits[46] == 0)
			{
				IVV = Convert.ToString(bin2decimal(array5) * 32);
				return;
			}
			int[] a3 = two_complement(array5);
			IVV = Convert.ToString(-bin2decimal(a3) * 32);
		}
		else
		{
			IVV = "NV";
		}
	}

	public void transf_coord()
	{
		CoordinatesWGS84 radarCoordinates = new CoordinatesWGS84(rad(41.0, 18.0, 2.5284, 0), rad(2.0, 6.0, 7.4095, 0), 27.257);
		double num = 27.257;
		double num2 = 0.0;
		if (Flight__Level != "N/A")
		{
			num2 = ((!(Convert.ToDouble(Flight__Level) <= 0.0)) ? (Convert.ToDouble(Flight__Level) * 0.3048 * 100.0) : 0.0);
		}
		double num3 = 12742000.0 * (num2 - num) + num2 * num2 - num * num - Convert.ToDouble(rho_m) * Convert.ToDouble(rho_m);
		double num4 = 2.0 * Convert.ToDouble(rho_m) * (6371000.0 + num);
		double num5 = Math.Asin(num3 / num4);
		CoordinatesPolar polarCoordinates = new CoordinatesPolar(Convert.ToDouble(rho_m), Convert.ToDouble(theta_rad), num5);
		GeoUtils geoUtils = new GeoUtils();
		double num6 = 41.11571111111111;
		double num7 = 1.6925027777777777;
		geoUtils.setCenterProjection(new CoordinatesWGS84(num6 * Math.PI / 180.0, num7 * Math.PI / 180.0, 0.0));
		if (!double.IsNaN(num5))
		{
			CoordinatesXYZ cartesianCoordinates = geoUtils.change_radar_spherical2radar_cartesian(polarCoordinates);
			CoordinatesXYZ c = geoUtils.change_radar_cartesian2geocentric(radarCoordinates, cartesianCoordinates);
			CoordinatesWGS84 coordinatesWGS = geoUtils.change_geocentric2geodesic(c);
			Latitud = Convert.ToString(decimal.Round(Convert.ToDecimal(coordinatesWGS.Lat * 180.0 / Math.PI), 8));
			Longitud = Convert.ToString(decimal.Round(Convert.ToDecimal(coordinatesWGS.Lon * 180.0 / Math.PI), 8));
			h__wgs84 = Convert.ToString(coordinatesWGS.Height);
			h__ft = Convert.ToString(3.28084 * coordinatesWGS.Height);
			lat = coordinatesWGS.Lat * 180.0 / Math.PI;
			lon = coordinatesWGS.Lon * 180.0 / Math.PI;
		}
	}

	public double rad(double d1, double d2, double d3, int ns)
	{
		double num = d1 + d2 / 60.0 + d3 / 3600.0;
		if (ns == 1)
		{
			num *= -1.0;
		}
		return num * Math.PI / 180.0;
	}

	public void inicio_variables()
	{
		SAC = "N/A";
		SIC = "N/A";
		Time = "N/A";
		TYP_020 = "N/A";
		SIM_020 = "N/A";
		RDP_020 = "N/A";
		SPI_020 = "N/A";
		RAB_020 = "N/A";
		TST_020 = "N/A";
		ERR_020 = "N/A";
		XPP_020 = "N/A";
		ME_020 = "N/A";
		MI_020 = "N/A";
		FOE_FRI_020 = "N/A";
		RHO = "N/A";
		THETA = "N/A";
		V_070 = "N/A";
		G_070 = "N/A";
		Mode__3A = "N/A";
		V_090 = "N/A";
		G_090 = "N/A";
		Flight__Level = "N/A";
		SRL_130 = "N/A";
		SRR_130 = "N/A";
		SAM_130 = "N/A";
		PRL_130 = "N/A";
		PAM_130 = "N/A";
		RPD_130 = "N/A";
		APD_130 = "N/A";
		Target__address = "N/A";
		Target__identification = "N/A";
		Mode__S = "N/A";
		MCP_STATUS = "N/A";
		MCP__ALT = "N/A";
		FMS_STATUS = "N/A";
		FMS__ALT = "N/A";
		BP_STATUS = "N/A";
		BP = "N/A";
		MODE__STATUS = "N/A";
		VNAV = "N/A";
		ALT_HOLD = "N/A";
		APP = "N/A";
		TARGET_ALT_STATUS = "N/A";
		TARGET_ALT_SOURCE = "N/A";
		RA_STATUS = "N/A";
		RA = "N/A";
		TTA_STATUS = "N/A";
		TTA = "N/A";
		GS_STATUS = "N/A";
		GS = "N/A";
		TAR_STATUS = "N/A";
		TAR = "N/A";
		TAS_STATUS = "N/A";
		TAS = "N/A";
		HDG_STATUS = "N/A";
		HDG = "N/A";
		IAS_STATUS = "N/A";
		IAS = "N/A";
		MACH_STATUS = "N/A";
		MACH = "N/A";
		BAR_STATUS = "N/A";
		BAR = "N/A";
		IVV_STATUS = "N/A";
		IVV = "N/A";
		Track__number = "N/A";
		X__Component = "N/A";
		Y__Component = "N/A";
		Ground__Speed_kt = "N/A";
		Heading = "N/A";
		CNF_170 = "N/A";
		RAD_170 = "N/A";
		DOU_170 = "N/A";
		MAH_170 = "N/A";
		CDM_170 = "N/A";
		TRE_170 = "N/A";
		GHO_170 = "N/A";
		SUP_170 = "N/A";
		TCC_170 = "N/A";
		Measured__Height = "N/A";
		COM_230 = "N/A";
		STAT_230 = "N/A";
		SI_230 = "N/A";
		MSCC_230 = "N/A";
		ARC_230 = "N/A";
		AIC_230 = "N/A";
		B1A_230 = "N/A";
		B1B_230 = "N/A";
		Latitud = "N/A";
		Longitud = "N/A";
		h__wgs84 = "N/A";
		h__ft = "N/A";
	}
}

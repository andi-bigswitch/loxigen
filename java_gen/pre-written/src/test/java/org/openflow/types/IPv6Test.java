package org.openflow.types;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.net.Inet6Address;
import java.net.InetAddress;
import java.net.UnknownHostException;

import org.jboss.netty.buffer.ChannelBuffers;
import org.junit.Test;
import org.openflow.exceptions.OFParseError;
import org.openflow.exceptions.OFShortRead;

public class IPv6Test {

    String[] testStrings = {
            "::",
            "::1",
            "ffe0::",
            "1:2:3:4:5:6:7:8"
    };
    
    String[] ipsWithMask = {
                            "1::1/80",
                            "1:2:3:4::/ffff:ffff:ffff:ff00::",
                            "ffff:ffee:1::/ff00:ff00:ff00:ff00::",
                            "8:8:8:8:8:8:8:8",
    };
    
    byte[][] masks = {
                    new byte[] { (byte)0xff, (byte)0xff, (byte)0xff, (byte)0xff, 
                                 (byte)0xff, (byte)0xff, (byte)0xff, (byte)0xff, 
                                 (byte)0xff, (byte)0xff, (byte)0x00, (byte)0x00, 
                                 (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00 },
                    new byte[] { (byte)0xff, (byte)0xff, (byte)0xff, (byte)0xff, 
                                 (byte)0xff, (byte)0xff, (byte)0xff, (byte)0x00, 
                                 (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, 
                                 (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00 },
                    new byte[] { (byte)0xff, (byte)0x00, (byte)0xff, (byte)0x00, 
                                 (byte)0xff, (byte)0x00, (byte)0xff, (byte)0x00, 
                                 (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, 
                                 (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00 },
                    new byte[] { (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, 
                                 (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, 
                                 (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, 
                                 (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00 }
    };
    
    boolean[] hasMask = {
                         true,
                         true,
                         true,
                         false
    };

    @Test
    public void testMasked() throws UnknownHostException {
        for(int i=0; i < ipsWithMask.length; i++ ) {
            OFValueType value = IPv6WithMask.ofPossiblyMasked(ipsWithMask[i]);
            if (value instanceof IPv6 && !hasMask[i]) {
                // Types OK, check values
                IPv6 ip = (IPv6)value;
                InetAddress inetAddress = InetAddress.getByName(ipsWithMask[i]);

                assertArrayEquals(ip.getBytes(), inetAddress.getAddress());
                assertEquals(ipsWithMask[i], ip.toString());
            } else if (value instanceof IPv6WithMask && hasMask[i]) {
                IPv6WithMask ip = null;
                try {
                    ip = (IPv6WithMask)value;
                } catch (ClassCastException e) {
                    fail("Invalid Masked<T> type.");
                }
                // Types OK, check values
                InetAddress inetAddress = InetAddress.getByName(ipsWithMask[i].substring(0, ipsWithMask[i].indexOf('/')));

                assertArrayEquals(ip.value.getBytes(), inetAddress.getAddress());
                assertEquals(ipsWithMask[i].substring(0, ipsWithMask[i].indexOf('/')), ip.value.toString());
                assertArrayEquals(masks[i], ip.mask.getBytes());
            } else if (value instanceof IPv6) {
                fail("Expected masked IPv6, got unmasked IPv6.");
            } else {
                fail("Expected unmasked IPv6, got masked IPv6.");
            }
        }
    }


    @Test
    public void testOfString() throws UnknownHostException {
        for(int i=0; i < testStrings.length; i++ ) {
            IPv6 ip = IPv6.of(testStrings[i]);
            InetAddress inetAddress = InetAddress.getByName(testStrings[i]);

            assertArrayEquals(ip.getBytes(), inetAddress.getAddress());
            assertEquals(testStrings[i], ip.toString());
        }
    }

    @Test
    public void testOfByteArray() throws UnknownHostException {
        for(int i=0; i < testStrings.length; i++ ) {
            byte[] bytes = Inet6Address.getByName(testStrings[i]).getAddress();
            IPv6 ip = IPv6.of(bytes);
            assertEquals(testStrings[i], ip.toString());
            assertArrayEquals(bytes, ip.getBytes());
        }
    }

    @Test
    public void testReadFrom() throws OFParseError, OFShortRead, UnknownHostException {
        for(int i=0; i < testStrings.length; i++ ) {
            byte[] bytes = Inet6Address.getByName(testStrings[i]).getAddress();
            IPv6 ip = IPv6.read16Bytes(ChannelBuffers.copiedBuffer(bytes));
            assertEquals(testStrings[i], ip.toString());
            assertArrayEquals(bytes, ip.getBytes());
        }
    }

    String[] invalidIPs = {
            "",
            ":",
            "1:2:3:4:5:6:7:8:9",
            "1:2:3:4:5:6:7:8:",
            "1:2:3:4:5:6:7:8g",
            "1:2:3:",
            "12345::",
            "1::3::8",
            "::3::"
    };

    @Test
    public void testInvalidIPs() throws OFParseError, OFShortRead {
        for(String invalid : invalidIPs) {
            try {
                IPv6.of(invalid);
                fail("Invalid IP "+invalid+ " should have raised IllegalArgumentException");
            } catch(IllegalArgumentException e) {
                // ok
            }
        }
    }

    @Test
    public void testZeroCompression() throws OFParseError, OFShortRead {
        assertEquals("::", IPv6.of("::").toString(true, false));
        assertEquals("0:0:0:0:0:0:0:0", IPv6.of("::").toString(false, false));
        assertEquals("0000:0000:0000:0000:0000:0000:0000:0000", IPv6.of("::").toString(false, true));
        assertEquals("1::4:5:6:0:8", IPv6.of("1:0:0:4:5:6:0:8").toString(true, false));
        assertEquals("1:0:0:4::8", IPv6.of("1:0:0:4:0:0:0:8").toString(true, false));
    }
}
